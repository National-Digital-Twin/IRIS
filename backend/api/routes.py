# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import configparser
import re
import uuid
from datetime import datetime
from typing import Annotated, List, Optional, Tuple

import requests
from access import AccessClient
from config import get_settings
from db import execute_with_timeout, get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from mappers import (map_bounded_buildings_response,
                     map_bounded_filterable_buildings_response,
                     map_building_details_for_bulk_download,
                     map_building_hot_summer_days_response,
                     map_building_icing_days_response,
                     map_building_sunlight_hours_response,
                     map_building_weather_summary_response,
                     map_building_wind_driven_rain_response,
                     map_epc_statistics_response, map_filter_summary_response,
                     map_flagged_buildings_response,
                     map_percentage_building_attributes_per_region_response,
                     map_single_building_response,
                     map_structure_unit_flag_history_response)
from models.dto_models import (AverageDailySunlightHoursPerArea,
                               AverageSapRatingPerLodgementDate,
                               BuildingAttributePercentagesPerRegion,
                               BuildingDetailsForBulkDownload,
                               BuildingDetailsForBulkDownloadSchema,
                               BuildingExtremeWeatherSummaryData,
                               BuildingExtremeWeatherSummarySchema,
                               BuildingHotSummerDaysData,
                               BuildingHotSummerDaysSchema,
                               BuildingIcingDaysData, BuildingIcingDaysSchema,
                               BuildingsAffectedByExtremeWeather,
                               BuildingsByDeprivationDimension,
                               BuildingSunlightHoursData,
                               BuildingSunlightHoursSchema,
                               BuildingWindDrivenRainData,
                               BuildingWindDrivenRainSchema, CountOfEpcRatings,
                               CountOfEpcRatingsPerRegion, DetailedBuilding,
                               DetailedBuildingSchema, EpcAndOsBuildingSchema,
                               EpcRatingCountsOvertime, EPCRatingsByCategory,
                               EpcStatistics, FilterableBuilding,
                               FilterableBuildingSchema, FilterSummary,
                               FuelTypesByBuildingType,
                               NumberOfInDateAndExpiredEpcs,
                               SapRatingTimelineDataPoint, SimpleBuilding)
from models.ies_models import (EDH, ClassificationEmum, IesAccount,
                               IesAssessment, IesAssessToBeFalse,
                               IesAssessToBeTrue, IesClass, IesEntity,
                               IesPerson, IesState, IesThing, ies)
from pydantic import AfterValidator, BaseModel
from query import (get_all_ngd_attributes_pg,
                   get_average_daily_sunlight_hours_query, get_building,
                   get_building_details_for_bulk_download_query,
                   get_buildings_affected_by_extreme_weather_data_query,
                   get_buildings_by_deprivation_dimension_query,
                   get_buildings_in_bounding_box_query,
                   get_count_of_epc_rating_by_area_level_query,
                   get_count_of_epc_rating_by_features_query,
                   get_count_of_epc_rating_query, get_county_names_query,
                   get_district_names_query, get_epc_attributes_pg,
                   get_epc_ratings_overtime_query,
                   get_filterable_buildings_in_bounding_box_query,
                   get_filtered_avg_sap_rating_overtime_query,
                   get_flag_history, get_flagged_buildings,
                   get_floor_for_building,
                   get_fuel_types_by_building_type_query,
                   get_fueltype_for_building,
                   get_hot_summer_days_data_for_building_query,
                   get_icing_days_data_for_building_query,
                   get_national_avg_sap_rating_overtime_query,
                   get_ngd_roof_aspect_areas_for_building,
                   get_ngd_roof_material_for_building,
                   get_ngd_roof_shape_for_building,
                   get_ngd_solar_panel_presence_for_building,
                   get_number_of_in_date_and_expired_epcs_query,
                   get_percentage_of_buildings_attributes_per_region_query,
                   get_region_names_query, get_roof_for_building,
                   get_sap_rating_overtime_by_area_query,
                   get_sap_rating_overtime_by_property_type_query,
                   get_statistics_for_wards,
                   get_sunlight_hours_data_for_building_query,
                   get_walls_and_windows_for_building, get_ward_names_query,
                   get_weather_summary_data_for_building_query,
                   get_wind_driven_rain_data_for_building_query)
from rdflib import Graph
from requests import codes, exceptions
from services.climate_service import (fetch_geojson_for_hot_summer_days,
                                      fetch_geojson_for_icing_days,
                                      fetch_geojson_for_sunlight_hours,
                                      fetch_geojson_for_wind_driven_rain)
from services.demographics_service import fetch_geojson_for_deprivation
from services.energy_performance_service import (
    fetch_geojson_for_energy_performance_by_counties,
    fetch_geojson_for_energy_performance_by_districts,
    fetch_geojson_for_energy_performance_by_regions,
    fetch_geojson_for_energy_performance_by_wards)
from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_headers as get_forwarding_headers
from utils import has_bindings, validate_geojson_polygon

AREA_LEVEL_PATTERN = "^(region|county|district|ward)$"
FEATURE_PATTERN = "^(glazing_types|fuel_types|wall_construction|wall_insulation|floor_construction|floor_insulation|roof_construction|roof_material|roof_insulation|roof_insulation_thickness|solar_panels|roof_aspect)$"

EPC_FIELDS = [
    "lodgement_date",
    "built_form",
    "structure_unit_type",
    "floor_construction",
    "floor_insulation",
    "roof_construction",
    "roof_insulation_location",
    "roof_insulation_thickness",
    "wall_construction",
    "wall_insulation",
    "window_glazing",
    "fueltype",
]

router = APIRouter()

config_settings = get_settings()

default_security_label = EDH(classification=ClassificationEmum.official)
data_uri_stub = config_settings.DATA_URI  # This can be overridden in use

ACCESS_API_CALL_ERROR = "Error calling Access, Internal Server Error"
IDENTITY_API_CALL_ERROR = "Error calling Identity API, Internal Server Error"
ISO_8601_URL = "http://iso.org/iso8601#"
APPLICATION_JSON = "application/json"

GeoJSONPolygon = Annotated[str, AfterValidator(validate_geojson_polygon)]

if config_settings.UPDATE_MODE == "KAFKA":
    from ia_map_lib import Adapter, Record, RecordUtils
    from ia_map_lib.sinks import KafkaSink

    knowledgeSink = KafkaSink(
        topic=config_settings.IES_TOPIC, broker=config_settings.BOOTSTRAP_SERVERS
    )
    knowledgeAdapter = Adapter(
        knowledgeSink, name="IoW Write-Back API", source_name="local data"
    )


def get_headers(security_labels):
    return RecordUtils.to_headers(
        {"Security-Label": security_labels, "Content-Type": "application/n-triples"}
    )


config = configparser.ConfigParser()
config.read("setup.cfg")
# The URIs used in the ontologies
ndt_ont = "http://ndtp.co.uk/ontology#"

access_url = f"{config_settings.ACCESS_PROTOCOL}://{config_settings.ACCESS_HOST}:{config_settings.ACCESS_PORT}{config_settings.ACCESS_PATH}"
jena_url = f"{config_settings.JENA_PROTOCOL}://{config_settings.JENA_URL}:{config_settings.JENA_PORT}"


def add_prefix(prefix, uri):
    prefix_dict[prefix] = uri


access_client = AccessClient(access_url, config_settings.DEV_MODE)
prefix_dict = {}
add_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")
add_prefix("dc", "http://purl.org/dc/elements/1.1/")
add_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
add_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
add_prefix("owl", "http://www.w3.org/2002/07/owl#")
add_prefix("ies", ies)
add_prefix("data", data_uri_stub)
add_prefix("ndt_ont", ndt_ont)
add_prefix("ndt", "http://ndtp.co.uk/data#")
add_prefix("gp", "https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn#")
add_prefix(
    "epc",
    "http://gov.uk/government/organisations/department-for-levelling-up-housing-and-communities/ontology/epc#",
)


def format_prefixes():
    prefixes = ""
    for prefix in prefix_dict:
        prefixes = prefixes + "PREFIX " + prefix + ": <" + prefix_dict[prefix] + ">\n"
    return prefixes


def shorten(uri):
    for prefix in prefix_dict:
        stub = prefix_dict[prefix]
        uri = uri.replace(stub, prefix + ":")
    return uri


def lengthen(uri):
    for prefix in prefix_dict:
        stub = prefix_dict[prefix]
        uri = uri.replace(prefix + ":", stub)
    return uri


def sanitize_for_message(value: str, max_len: int = 200) -> str:
    if value is None:
        return ""
    trimmed = value.replace("\r", " ").replace("\n", " ").strip()
    clipped = trimmed[:max_len]
    return re.sub(r"[^a-zA-Z0-9 .,:;@/_+-]", "?", clipped)


prefixes = format_prefixes()

# Test person is created so we can assign assessments to someone. Once access to user info is available, this will be replaced with the logged in user. i.e. this is just a temporary fix for testing purposes.
test_person_uri = data_uri_stub + "TestUser"


# Checks to see if an iesThing has a URI - if not, it mints a new uri using the data_uri_stub
# Also checks if a security label has been set
def mint_uri(item: IesThing):
    if item.uri is None:
        item.uri = data_uri_stub + str(uuid.uuid4())
    if item.securityLabel is None:
        item.securityLabel = default_security_label
    return item


# Local dictionaries that are used to check that certain classes exist before posting references to them
assessment_classes = {}
building_state_classes = {}


def run_sparql_query(
    query: str, headers: dict[str, str], query_dataset=config_settings.DATASET
):
    global jena_url
    get_uri = jena_url + "/" + query_dataset + "/query"
    try:
        response = requests.get(
            get_uri, params={"query": prefixes + query}, headers=headers
        )
        response.raise_for_status()
        return response.json()
    except exceptions.HTTPError as e:
        raise HTTPException(e.response.status_code)


def run_sparql_update(
    query: str, forwarding_headers: dict[str, str] = {}, security_label=None
):
    global jena_url, default_security_label
    sec_label = security_label

    if sec_label is None:
        sec_label = default_security_label
    if config_settings.UPDATE_MODE == "SCG":
        post_uri = jena_url + "/" + config_settings.DATASET + "/update"
        headers = {
            "Accept": "*/*",
            "Security-Label": sec_label.to_string(),
            "Content-Type": "application/sparql-update",
            **forwarding_headers,
        }
        try:
            requests.post(post_uri, headers=headers, data=prefixes + query)
        except exceptions.HTTPError as e:
            raise HTTPException(e.response.status_code)
    elif config_settings.UPDATE_MODE == "KAFKA":
        g = Graph()
        g.update(query)
        out_data = g.serialize(format="nt")
        try:
            record = Record(get_headers(sec_label.to_string()), None, out_data)
            knowledgeAdapter.send(record)
        except Exception as e:
            print(e)
            raise e
    else:
        raise ValueError("unknown update mode: " + config_settings.UPDATE_MODE)


def _build_exclusion_filter_clause(exclude_super) -> str:
    if exclude_super is None or exclude_super == "":
        return ""
    return f"""FILTER NOT EXISTS {{ ?sub rdfs:subClassOf* <{exclude_super}>  }}  """


def _append_unique(items: list, value) -> None:
    if value not in items:
        items.append(value)


def get_subtypes(super_class, headers: dict[str, str], exclude_super=None):
    sub_classes = {}
    filter_clause = _build_exclusion_filter_clause(exclude_super)

    results = run_sparql_query(
        f"""
        SELECT ?sub ?parent ?comment WHERE
            {{
                ?sub rdfs:subClassOf* <{super_class}> .
                ?sub rdfs:subClassOf ?parent .
                OPTIONAL {{ ?sub rdfs:comment ?comment}}
                {filter_clause}
            }}""",
        headers,
        query_dataset=config_settings.ONTO_DATASET,
    )

    bindings = (((results or {}).get("results") or {}).get("bindings")) or []
    for sub in bindings:
        sub_uri = sub["sub"]["value"]
        # create a new empty(ish) item
        my_obj = sub_classes.setdefault(
            sub_uri,
            {
                "uri": sub_uri,
                "shortName": shorten(sub_uri),
                "superClasses": [],
                "description": [],
            },
        )

        comment = (sub.get("comment") or {}).get("value")
        if "comment" in sub:
            # If there are any comments, append them
            _append_unique(my_obj["description"], comment)

        # There may be more than one parent, so append them as we find them
        _append_unique(my_obj["superClasses"], sub["parent"]["value"])

    sub_list = [
        {
            "uri": key,
            "shortName": sub["shortName"],
            "superClasses": sub["superClasses"],
            "description": sub["description"],
        }
        for key, sub in sub_classes.items()
    ]

    return sub_classes, sub_list


def create_person_insert(user_id, username):
    names = username.split(" ")
    uri = data_uri_stub + user_id
    return (
        uri,
        f"""
        <{uri}> a ies:Person .
        <{uri}> ies:hasName <{uri + "_NAME"}> .
        <{uri + "_NAME"}> a ies:PersonName .
        <{uri + "_NAME"}> ies:representationValue "{names[0]} {names[1]}" .
        <{uri + "_SURNAME"}> a ies:Surname .
        <{uri + "_SURNAME"}> ies:inRepresentation <{uri + "_NAME"}> .
        <{uri + "_SURNAME"}> ies:representationValue "{names[1]}" .
        <{uri + "_GIVENNAME"}> a ies:GivenName .
        <{uri + "_GIVENNAME"}> ies:inRepresentation <{uri + "_NAME"}> .
        <{uri + "_GIVENNAME"}> ies:representationValue "{names[0]}" .
    """,
    )


@router.get("/test-user-passthrough")
def test_user(request: Request):
    try:
        user = access_client.get_user_details(request.headers)
        pi = create_person_insert(user["user_id"], user["username"])
        return [user, pi]
    except exceptions.HTTPError as e:
        raise HTTPException(e.response.status_code)


@router.get("/version-info")
def version():
    return config["metadata"]


@router.post("/test-post")
def test_post(req: Request):
    print("testing post")
    return Response()


@router.get("/")
def read_root():
    return {"ok": True}


@router.get(
    "/assessment-classes",
    response_model=List[IesClass],
    description="returns all the subclasses of ies:Assessment that are in the ontology",
)
def get_assessments(req: Request):
    sub_classes, sub_list = get_subtypes(
        ies + "Assessment", get_forwarding_headers(req.headers)
    )
    global assessment_classes
    assessment_classes = sub_classes
    return sub_list


@router.get(
    "/buildings/states/classes",
    response_model=List[IesClass],
    description="returns all the subclasses of BuildingState that are in the ontology",
)
def get_building_state_classes(req: Request):
    sub_classes, sub_list = get_subtypes(
        ndt_ont + "BuildingState",
        get_forwarding_headers(req.headers),
        exclude_super=ies + "Location",
    )
    global building_state_classes
    building_state_classes = sub_classes
    return sub_list


# @app.post("/people",description="Creates a new Person")
def post_person(per: IesPerson):
    mint_uri(per)
    query = f"""
    {format_prefixes()}
    INSERT DATA
            {{
                <{per.uri}> a ies:Person .
                <{per.uri}> ies:hasName <{per.uri + "_NAME"}> .
                <{per.uri + "_NAME"}> a ies:PersonName .
                <{per.uri + "_SURNAME"}> a ies:Surname .
                <{per.uri + "_SURNAME"}> ies:inRepresentation <{per.uri + "_NAME"}> .
                <{per.uri + "_SURNAME"}> ies:representationValue "{per.surname}" .
                <{per.uri + "_GIVENNAME"}> a ies:GivenName .
                <{per.uri + "_GIVENNAME"}> ies:inRepresentation <{per.uri + "_NAME"}> .
                <{per.uri + "_GIVENNAME"}> ies:representationValue "{per.givenName}" .
            }}"""
    run_sparql_update(query=query, security_label=per.securityLabel)
    return per.uri


@router.get("/dashboard/epc-ratings", response_model=List[CountOfEpcRatings])
async def get_epc_ratings_for_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_count_of_epc_rating_query(
        polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)
    mapped_results = [CountOfEpcRatings.from_orm(row) for row in results]

    return mapped_results


@router.get(
    "/dashboard/epc-ratings-per-region", response_model=List[CountOfEpcRatingsPerRegion]
)
async def get_epc_ratings_per_region_for_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_count_of_epc_rating_query(
        per_region=True, polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)
    mapped_results = [CountOfEpcRatingsPerRegion.from_orm(row) for row in results]

    return mapped_results


@router.get(
    "/dashboard/epc-ratings-by-area-level", response_model=List[EPCRatingsByCategory]
)
async def get_epc_ratings_by_area_level_for_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    group_by_level: Annotated[str, Query(..., pattern=AREA_LEVEL_PATTERN)],
    filter_area_level: Annotated[
        Optional[str], Query(pattern=AREA_LEVEL_PATTERN)
    ] = None,
    filter_area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_count_of_epc_rating_by_area_level_query(
        group_by_level=group_by_level,
        filter_area_level=filter_area_level,
        filter_area_names=filter_area_names,
    )
    results = await db.execute(text(query), params)

    return [EPCRatingsByCategory.from_orm(row) for row in results]


@router.get(
    "/dashboard/epc-ratings-by-feature", response_model=List[EPCRatingsByCategory]
)
async def get_epc_ratings_by_feature_for_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    feature: Annotated[str, Query(..., pattern=FEATURE_PATTERN)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_count_of_epc_rating_by_features_query(
        feature=feature, polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)

    return [EPCRatingsByCategory.from_orm(row) for row in results]


@router.get(
    "/dashboard/building-attributes-percentage-per-region",
    response_model=List[BuildingAttributePercentagesPerRegion],
)
async def get_percentage_building_attributes_per_region(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_percentage_of_buildings_attributes_per_region_query(
        polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)

    return map_percentage_building_attributes_per_region_response(results)


@router.get(
    "/dashboard/sap-rating-overtime",
    response_model=List[AverageSapRatingPerLodgementDate],
)
async def get_sap_rating_overtime(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    national_query = get_national_avg_sap_rating_overtime_query()
    national_results = await db.execute(text(national_query))

    results_by_date = {
        row.date: AverageSapRatingPerLodgementDate(
            date=row.date,
            national_avg_sap_rating=row.avg_sap_rating,
            filtered_avg_sap_rating=None,
        )
        for row in national_results
    }

    if polygon or (area_level and area_names):
        filtered_query, params = get_filtered_avg_sap_rating_overtime_query(
            polygon=polygon, area_level=area_level, area_names=area_names
        )
        filtered_results = await db.execute(text(filtered_query), params)

        for row in filtered_results:
            if row.date in results_by_date:
                results_by_date[row.date].filtered_avg_sap_rating = row.avg_sap_rating

    return list(results_by_date.values())


@router.get(
    "/dashboard/sap-rating-overtime-by-property-type",
    response_model=List[SapRatingTimelineDataPoint],
)
async def get_sap_rating_overtime_by_property_type(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[GeoJSONPolygon, Query(...)],
):
    query, params = get_sap_rating_overtime_by_property_type_query(polygon=polygon)
    results = await db.execute(text(query), params)
    return [SapRatingTimelineDataPoint.from_orm(row) for row in results]


@router.get(
    "/dashboard/sap-rating-overtime-by-area",
    response_model=List[SapRatingTimelineDataPoint],
)
async def get_sap_rating_overtime_by_area(
    db: Annotated[AsyncSession, Depends(get_db)],
    group_by_level: Annotated[str, Query(..., pattern=AREA_LEVEL_PATTERN)],
    filter_area_level: Annotated[
        Optional[str], Query(pattern=AREA_LEVEL_PATTERN)
    ] = None,
    filter_area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_sap_rating_overtime_by_area_query(
        group_by_level=group_by_level,
        filter_area_level=filter_area_level,
        filter_area_names=filter_area_names,
    )
    results = await db.execute(text(query), params)
    return [SapRatingTimelineDataPoint.from_orm(row) for row in results]


@router.get(
    "/dashboard/epc-ratings-overtime",
    response_model=List[EpcRatingCountsOvertime],
)
async def get_epc_ratings_overtime(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_epc_ratings_overtime_query(
        polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)
    mapped_results = [EpcRatingCountsOvertime.from_orm(row) for row in results]

    return mapped_results


@router.get(
    "/dashboard/fuel-types-by-building-type",
    response_model=List[FuelTypesByBuildingType],
)
async def get_fuel_types_by_building_type(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_fuel_types_by_building_type_query(
        polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)
    mapped_results = [FuelTypesByBuildingType.from_orm(row) for row in results]

    return mapped_results


@router.get(
    "/dashboard/buildings-affected-by-extreme-weather",
    response_model=List[BuildingsAffectedByExtremeWeather],
)
async def get_buildings_affected_by_extreme_weather(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    has_filter = bool(polygon or (area_level and area_names))
    query, params = get_buildings_affected_by_extreme_weather_data_query(
        polygon=polygon, area_level=area_level, area_names=area_names
    )

    results = await db.execute(text(query), params)
    mapped_results = [
        BuildingsAffectedByExtremeWeather.from_orm(row, has_filter=has_filter)
        for row in results
    ]

    return mapped_results


@router.get(
    "/dashboard/no-of-in-date-and-expired-epcs",
    response_model=List[NumberOfInDateAndExpiredEpcs],
)
async def get_number_of_in_date_and_expired_epcs(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_number_of_in_date_and_expired_epcs_query(
        polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)
    mapped_results = [NumberOfInDateAndExpiredEpcs.from_orm(row) for row in results]

    return mapped_results


@router.get(
    "/dashboard/buildings-by-deprivation-dimension",
    response_model=List[BuildingsByDeprivationDimension],
)
async def get_buildings_by_deprivation_dimension_for_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
):
    query, params = get_buildings_by_deprivation_dimension_query(
        polygon=polygon, area_level=area_level, area_names=area_names
    )
    results = await db.execute(text(query), params)
    mapped_results = [BuildingsByDeprivationDimension.from_orm(row) for row in results]

    return mapped_results


@router.get(
    "/dashboard/average-daily-sunlight-hours-by-area-level",
    response_model=List[AverageDailySunlightHoursPerArea],
)
async def get_average_daily_sunlight_hours(
    db: Annotated[AsyncSession, Depends(get_db)],
    group_by_level: Annotated[str, Query(..., pattern=AREA_LEVEL_PATTERN)],
    area_level: Annotated[Optional[str], Query(pattern=AREA_LEVEL_PATTERN)] = None,
    area_names: Annotated[Optional[List[str]], Query()] = None,
    polygon: Annotated[Optional[GeoJSONPolygon], Query()] = None,
):
    query, params = get_average_daily_sunlight_hours_query(
        group_by_level=group_by_level, area_level=area_level, area_names=area_names, polygon=polygon
    )
    results = await db.execute(text(query), params)
    mapped_results = [
        AverageDailySunlightHoursPerArea.from_orm(row) for row in results
    ]

    return mapped_results


@router.get(
    "/buildings",
    response_model=List[SimpleBuilding],
    description="Gets all the buildings inside a bounding box along with their types, TOIDs, UPRNs, and current energy ratings",
)
async def get_buildings_in_bounding_box(
    min_long: float,
    max_long: float,
    min_lat: float,
    max_lat: float,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    buildings_in_bounding_box_results = await db.execute(
        text(get_buildings_in_bounding_box_query()),
        {
            "min_long": min_long,
            "max_long": max_long,
            "min_lat": min_lat,
            "max_lat": max_lat,
            "srid": 4326,
        },
    )
    results = [
        EpcAndOsBuildingSchema.from_orm(result)
        for result in buildings_in_bounding_box_results
    ]
    return map_bounded_buildings_response(results)


@router.get(
    "/filter-summary",
    response_model=FilterSummary,
    description="Get all the filters available inside a bounding box",
)
async def get_filter_summary(
    min_long: float,
    max_long: float,
    min_lat: float,
    max_lat: float,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    detailed_buildings_in_bounding_box_results = await execute_with_timeout(
        db,
        text(get_filterable_buildings_in_bounding_box_query()),
        timeout_seconds=60,
        params={
            "min_long": min_long,
            "max_long": max_long,
            "min_lat": min_lat,
            "max_lat": max_lat,
            "srid": 4326,
        },
    )

    results = [
        FilterableBuildingSchema.from_orm(result)
        for result in detailed_buildings_in_bounding_box_results
    ]
    return map_filter_summary_response(results)


@router.get(
    "/filterable-buildings",
    response_model=List[FilterableBuilding],
    description="Gets all the buildings inside a bounding box along with detailed metadata e.g. floor construction, wall insulation, window glazing that can be used for filtering",
)
async def get_filterable_buildings_in_bounding_box(
    min_long: float,
    max_long: float,
    min_lat: float,
    max_lat: float,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    filterable_buildings_in_bounding_box_results = await db.execute(
        text(get_filterable_buildings_in_bounding_box_query()),
        {
            "min_long": min_long,
            "max_long": max_long,
            "min_lat": min_lat,
            "max_lat": max_lat,
            "srid": 4326,
        },
    )
    results = [
        FilterableBuildingSchema.from_orm(result)
        for result in filterable_buildings_in_bounding_box_results
    ]
    return map_bounded_filterable_buildings_response(results)


@router.get(
    "/epc-statistics/wards",
    response_model=List[EpcStatistics],
    description="Gets the statistics for all wards",
)
def get_epc_statistics_for_wards(req: Request):
    query = get_statistics_for_wards()
    results = run_sparql_query(query, get_forwarding_headers(req.headers))
    return map_epc_statistics_response(results)


class InvalidateFlag(BaseModel):
    flagUri: str
    assessmentTypeOverride: str = prefix_dict["ndt_ont"] + "AssessToBeFalse"
    securityLabel: EDH = default_security_label


# @router.post(
#     "/invalidate-flag",
#     description="Post to this endpoint to invalidate an existing flag.",
#     response_model=str,
#     responses={
#         422: {
#             "description": "assessmentTypeOverride must be a subclass of ndt_ont:AssessToBeFalse"
#         },
#         500: {
#             "description": ACCESS_API_CALL_ERROR,
#         },
#     },
# )
def invalidate_flag(request: Request, invalid: InvalidateFlag):
    try:
        user = access_client.get_user_details(request.headers)
    except exceptions.RequestException as e:
        if e.response is not None:
            reason = sanitize_for_message(e.response.reason)
            raise HTTPException(
                e.response.status_code, f"Error calling Access:{reason}"
            )
        else:
            raise HTTPException(500, ACCESS_API_CALL_ERROR)
    assessor, person = create_person_insert(user["user_id"], user["username"])
    assessment_time = ISO_8601_URL + datetime.now().isoformat()
    assessment = data_uri_stub + str(uuid.uuid4())
    assessment_subclasses, _ = get_subtypes(
        prefix_dict["ndt_ont"] + "AssessToBeFalse",
        get_forwarding_headers(request.headers),
    )

    if (
        invalid.assessmentTypeOverride != prefix_dict["ndt_ont"] + "AssessToBeFalse"
        and lengthen(invalid.assessmentTypeOverride) not in assessment_subclasses
    ):
        raise HTTPException(
            422, "assessmentTypeOverride must be a subclass of ndt_ont:AssessToBeFalse"
        )
    query = f"""
        {format_prefixes()}
        INSERT DATA {{
            <{assessment}> a <{lengthen(invalid.assessmentTypeOverride)}> .
            <{assessment}> ies:assessor <{assessor}> .
            {person}
            <{assessment}> ies:assessed <{lengthen(invalid.flagUri)}> .
            <{assessment}> ies:inPeriod <{assessment_time}> .
        }}
    """
    run_sparql_update(query=query, security_label=invalid.securityLabel)
    return assessment


def is_missing(value):
    return value is None or value == "" or value == "NoData"


def apply_epc_fallback(building: DetailedBuilding, pg_row):

    updates = {
        "post_code": pg_row.post_code,
        "lodgement_date": str(pg_row.lodgement_date) if pg_row.lodgement_date else None,
        "sap_rating": pg_row.sap_rating,
        "built_form": pg_row.built_form,
        "structure_unit_type": pg_row.structure_unit_type,
        "floor_construction": pg_row.floor_construction,
        "floor_insulation": pg_row.floor_insulation,
        "roof_construction": pg_row.roof_construction,
        "roof_insulation_location": pg_row.roof_insulation_location,
        "roof_insulation_thickness": pg_row.roof_insulation_thickness,
        "wall_construction": pg_row.wall_construction,
        "wall_insulation": pg_row.wall_insulation,
        "window_glazing": pg_row.window_glazing,
        "fueltype": pg_row.fuel_type,
    }

    for field, value in updates.items():
        if is_missing(getattr(building, field)) and not is_missing(value):
            setattr(building, field, value)


def _or_fallback(current_result, fallback_result):
    return current_result if has_bindings(current_result) else fallback_result


def _ngd_roof_aspect_area_fallback(pg_row: DetailedBuildingSchema) -> dict:
    return {
        "roof_aspect_area_facing_north_m2": pg_row.roof_aspect_area_facing_north_m2,
        "roof_aspect_area_facing_north_east_m2": pg_row.roof_aspect_area_facing_north_east_m2,
        "roof_aspect_area_facing_east_m2": pg_row.roof_aspect_area_facing_east_m2,
        "roof_aspect_area_facing_south_east_m2": pg_row.roof_aspect_area_facing_south_east_m2,
        "roof_aspect_area_facing_south_m2": pg_row.roof_aspect_area_facing_south_m2,
        "roof_aspect_area_facing_south_west_m2": pg_row.roof_aspect_area_facing_south_west_m2,
        "roof_aspect_area_facing_west_m2": pg_row.roof_aspect_area_facing_west_m2,
        "roof_aspect_area_facing_north_west_m2": pg_row.roof_aspect_area_facing_north_west_m2,
        "roof_aspect_area_indeterminable_m2": pg_row.roof_aspect_area_indeterminable_m2,
    }


async def _apply_ngd_pg_fallback_if_needed(
    uprn: str,
    db: AsyncSession,
    ngd_roof_material_results: dict,
    ngd_solar_panel_presence_results: dict,
    ngd_roof_shape_results: dict,
    ngd_roof_aspect_areas_results: dict,
) -> Tuple[dict, dict, dict, dict]:
    fallback_required = any(
        not has_bindings(result)
        for result in (
            ngd_roof_material_results,
            ngd_solar_panel_presence_results,
            ngd_roof_shape_results,
            ngd_roof_aspect_areas_results,
        )
    )
    if not fallback_required:
        return (
            ngd_roof_material_results,
            ngd_solar_panel_presence_results,
            ngd_roof_shape_results,
            ngd_roof_aspect_areas_results,
        )

    data = await db.execute(text(get_all_ngd_attributes_pg()), {"uprn": uprn})
    rows = [DetailedBuildingSchema.from_orm(row) for row in data]
    if len(rows) != 1:
        return (
            ngd_roof_material_results,
            ngd_solar_panel_presence_results,
            ngd_roof_shape_results,
            ngd_roof_aspect_areas_results,
        )

    pg = rows[0]
    return (
        _or_fallback(ngd_roof_material_results, {"roof_material": pg.roof_material}),
        _or_fallback(
            ngd_solar_panel_presence_results,
            {"solar_panel_presence": pg.solar_panel_presence},
        ),
        _or_fallback(ngd_roof_shape_results, {"roof_shape": pg.roof_shape}),
        _or_fallback(
            ngd_roof_aspect_areas_results, _ngd_roof_aspect_area_fallback(pg)
        ),
    )


async def _apply_epc_pg_fallback_if_needed(
    building: DetailedBuilding, uprn: str, db: AsyncSession
) -> None:
    if not any(is_missing(getattr(building, field)) for field in EPC_FIELDS):
        return

    geonode_results = await db.execute(text(get_epc_attributes_pg()), {"uprn": uprn})
    geonode_row = geonode_results.first()
    if geonode_row:
        apply_epc_fallback(building, geonode_row)


@router.get(
    "/buildings/{uprn}",
    response_model=DetailedBuilding,
    description="returns the building that corresponds to the provided UPRN",
)
async def get_building_by_uprn(
    uprn: str,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    building_results = run_sparql_query(
        get_building(uprn), get_forwarding_headers(req.headers)
    )
    roof_results = run_sparql_query(
        get_roof_for_building(uprn), get_forwarding_headers(req.headers)
    )
    floor_results = run_sparql_query(
        get_floor_for_building(uprn), get_forwarding_headers(req.headers)
    )
    wall_window_results = run_sparql_query(
        get_walls_and_windows_for_building(uprn), get_forwarding_headers(req.headers)
    )
    fueltype_results = run_sparql_query(
        get_fueltype_for_building(uprn), get_forwarding_headers(req.headers)
    )
    ngd_roof_material_results = run_sparql_query(
        get_ngd_roof_material_for_building(uprn), get_forwarding_headers(req.headers)
    )
    ngd_solar_panel_presence_results = run_sparql_query(
        get_ngd_solar_panel_presence_for_building(uprn),
        get_forwarding_headers(req.headers),
    )
    ngd_roof_shape_results = run_sparql_query(
        get_ngd_roof_shape_for_building(uprn), get_forwarding_headers(req.headers)
    )
    ngd_roof_aspect_areas_results = run_sparql_query(
        get_ngd_roof_aspect_areas_for_building(uprn),
        get_forwarding_headers(req.headers),
    )

    (
        ngd_roof_material_results,
        ngd_solar_panel_presence_results,
        ngd_roof_shape_results,
        ngd_roof_aspect_areas_results,
    ) = await _apply_ngd_pg_fallback_if_needed(
        uprn,
        db,
        ngd_roof_material_results,
        ngd_solar_panel_presence_results,
        ngd_roof_shape_results,
        ngd_roof_aspect_areas_results,
    )

    building = map_single_building_response(
        uprn,
        building_results,
        roof_results,
        floor_results,
        wall_window_results,
        fueltype_results,
        ngd_roof_material_results,
        ngd_solar_panel_presence_results,
        ngd_roof_shape_results,
        ngd_roof_aspect_areas_results,
    )

    await _apply_epc_pg_fallback_if_needed(building, uprn, db)

    return building


# @router.get(
#     "/buildings/{uprn}/flag-history",
#     response_model=list[FlagHistory],
#     description="Gets the flagging and assessment history for a specific building identified by its UPRN",
# )
def get_building_flag_history(uprn: str, req: Request):
    query = get_flag_history(uprn)
    results = run_sparql_query(query, get_forwarding_headers(req.headers))
    return map_structure_unit_flag_history_response(results)


# @router.get(
#     "/flagged-buildings",
#     description="Gets all buildings that have been flagged",
#     response_model=list[FlaggedBuilding],
# )
def get_all_flagged_buildings(req: Request):
    query = get_flagged_buildings()
    results = run_sparql_query(query, get_forwarding_headers(req.headers))
    return map_flagged_buildings_response(results)


# @router.post(
#     "/flag-to-investigate",
#     description="Add a flag to an Entity instance as being worth investigating- URI of Entity must be provided",
#     response_model=str,
#     responses={
#         422: {"description": "URI of flagged entity must be provided"},
#         500: {"description": ACCESS_API_CALL_ERROR},
#     },
# )
def post_flag_investigate(request: Request, visited: IesEntity):
    if not visited or not visited.uri:
        raise HTTPException(422, "URI of flagged entity must be provided")
    try:
        user = access_client.get_user_details(request.headers)
    except exceptions.RequestException as e:
        if e.response is not None:
            reason = sanitize_for_message(e.response.reason)
            raise HTTPException(
                e.response.status_code, f"Error calling Access:{reason}"
            )
        else:
            raise HTTPException(500, ACCESS_API_CALL_ERROR)

    flagger, person = create_person_insert(user["user_id"], user["username"])

    flag_time = ISO_8601_URL + datetime.now().isoformat()
    flag_state = data_uri_stub + str(uuid.uuid4())
    query = f"""
        {format_prefixes()}
        INSERT DATA {{
            <{flag_state}> ies:interestedIn <{lengthen(visited.uri)}> .
            <{flag_state}> ies:isStateOf <{flagger}> .
            {person}
            <{flag_state}> ies:inPeriod <{flag_time}> .
            <{flag_state}> a ndt:InterestedInInvestigating .
        }}
    """
    run_sparql_update(
        query=query,
        forwarding_headers=get_forwarding_headers(request.headers),
        security_label=visited.securityLabel,
    )
    return flag_state


@router.get("/data/climate/wind-driven-rain")
async def get_wind_driven_rain_data(
    geojson: Annotated[Tuple, Depends(fetch_geojson_for_wind_driven_rain)],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/climate/icing-days")
async def get_icing_days_data(
    geojson: Annotated[Tuple, Depends(fetch_geojson_for_icing_days)],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/climate/hot-summer-days")
async def get_hot_summer_days_data(
    geojson: Annotated[Tuple, Depends(fetch_geojson_for_hot_summer_days)],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/climate/sunlight-hours")
async def get_sunlight_hours_data(
    geojson: Annotated[Tuple, Depends(fetch_geojson_for_sunlight_hours)],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/demographics/deprivation")
async def get_deprivation_data(
    geojson: Annotated[Tuple, Depends(fetch_geojson_for_deprivation)],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/energy-performance/wards")
async def get_energy_performance_data_by_wards(
    geojson: Annotated[Tuple, Depends(fetch_geojson_for_energy_performance_by_wards)],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/energy-performance/districts")
async def get_energy_performance_data_by_districts(
    geojson: Annotated[
        Tuple, Depends(fetch_geojson_for_energy_performance_by_districts)
    ],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/energy-performance/counties")
async def get_energy_performance_data_by_counties(
    geojson: Annotated[
        Tuple, Depends(fetch_geojson_for_energy_performance_by_counties)
    ],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/data/energy-performance/regions")
async def get_energy_performance_data_by_regions(
    geojson: Annotated[Tuple, Depends(fetch_geojson_for_energy_performance_by_regions)],
):
    return Response(content=geojson, media_type=APPLICATION_JSON)


@router.get("/areas/regions", response_model=List[str])
async def get_regions(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get list of all distinct region names."""
    query = get_region_names_query()
    result = await db.execute(text(query))
    return [row[0] for row in result]


@router.get("/areas/counties", response_model=List[str])
async def get_counties(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get list of all distinct county names."""
    query = get_county_names_query()
    result = await db.execute(text(query))
    return [row[0] for row in result]


@router.get("/areas/districts", response_model=List[str])
async def get_districts(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get list of all distinct district names."""
    query = get_district_names_query()
    result = await db.execute(text(query))
    return [row[0] for row in result]


@router.get("/areas/wards", response_model=List[str])
async def get_wards(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get list of all distinct ward names."""
    query = get_ward_names_query()
    result = await db.execute(text(query))
    return [row[0] for row in result]


# @app.post("/buildings/states",description="Add a new state to a building")
def post_building_state(bs: IesState):
    if bs.stateType not in building_state_classes:
        # get_building_states()
        if bs.stateType not in building_state_classes:
            safe_type = sanitize_for_message(bs.stateType)
            raise HTTPException(
                status_code=404,
                detail=f"Building State Class: {safe_type} not found",
            )
    mint_uri(bs)
    if bs.startDateTime:
        start_date = ISO_8601_URL + bs.startDateTime.isoformat().replace(" ", "T")
        start_sparql = f"""
                <{bs.uri}_start> a ies:BoundingState .
                <{bs.uri}_start> ies:isStartOf <{bs.uri}> .
                <{bs.uri}_start> ies:inPeriod <{start_date}> .
        """
    else:
        start_sparql = """"""

    if bs.endDateTime:
        end_date = ISO_8601_URL + bs.startDateTime.isoformat().replace(" ", "T")
        end_sparql = f"""
                <{bs.uri}_end> a ies:BoundingState .
                <{bs.uri}_end> ies:isEndOf <{bs.uri}> .
                <{bs.uri}_end> ies:inPeriod <{end_date}> .
        """
    else:
        end_sparql = """"""

    query = f"""INSERT DATA
            {{
                <{bs.uri}> a <{bs.stateType}> .
                <{bs.uri}> ies:isStateOf <{bs.stateOf}> .
                {start_sparql}
                {end_sparql}
            }}"""
    run_sparql_update(query=query, security_label=bs.securityLabel)
    return bs.uri


# @app.post("/accounts")
def post_account(acc: IesAccount):
    if acc.uri is None:
        acc.uri = data_uri_stub + "Account-" + acc.id
    if acc.email is not None:
        email_sparql = f"""
            <{acc.uri + "email"}> a ies:EmailAddress .
            <{acc.uri + "email"}> ies:representationValue "{acc.email}" .
            <{acc.uri}> ies:isIdentifiedBy <{acc.uri + "email"}> .
        """
    else:
        email_sparql = """"""

    if acc.name is not None:
        name_sparql = f"""
            <{acc.uri + "name"}> a ies:Name .
            <{acc.uri + "name"}> ies:representationValue "{acc.name}" .
            <{acc.uri}> ies:hasName <{acc.uri + "name"}> .
        """
    else:
        name_sparql = """"""

    query = f"""INSERT DATA
        {{
            <{acc.uri}> a ies:Account .
            <{acc.uri + "ID"}> a ies:AccountNumber .
            <{acc.uri + "ID"}> ies:representationValue "{acc.id}" .
            <{acc.uri}> ies:isIdentifiedBy <{acc.uri + "ID"}> .
            {email_sparql}
            {name_sparql}
        }}"""
    run_sparql_update(query=query, security_label=acc.securityLabel)
    return acc.uri


def assess(ass: IesAssessment):
    mint_uri(ass)
    if ass.inPeriod is None:
        ass.inPeriod = datetime.datetime.now().isoformat()
    if ass.assessor is None:
        ass.assessor = test_person_uri

    type_str = ""
    for typ in ass.types:
        type_str = type_str + f"<{ass.uri}> a <{typ}> . "
    query = f"""INSERT DATA
            {{
                {type_str}
                <{ass.uri}> ies:assessed <{ass.assessedItem}> .
                <{ass.uri}> ies:assessor <{ass.assessor}> .
                <{ass.uri}> ies:inPeriod "{ass.inPeriod}"
            }}"""
    run_sparql_update(query=query, security_label=ass.securityLabel)

    return ass.uri


# @app.post("/assessments/assess-to-be-true")
def post_assess_to_be_true(ass: IesAssessToBeTrue):
    return assess(ass)


# @app.post("/assessments/assess-to-be-false")
def post_assess_to_be_false(ass: IesAssessToBeFalse):
    return assess(ass)


@router.post(
    "/uri-stub",
    description="Sets the default uri stub used by the API when generating data uris - it will append a UUID to the stub for every URI it creates",
    status_code=204,
)
def post_uri_stub(uri: str):
    global data_uri_stub
    data_uri_stub = uri
    return sanitize_for_message(data_uri_stub, max_len=512)


@router.get(
    "/uri-stub",
    description="Gets the  default uri stub used by the API when generating data uris",
)
def get_uri_stub():
    return data_uri_stub


@router.post(
    "/default-security-label",
    description="Sets the default security label used when writing data",
    status_code=204,
)
def post_default_security_label(label: EDH):
    global default_security_label
    default_security_label = label


@router.get(
    "/default-security-label",
    description="Gets the default security label used when writing data",
    response_model=EDH,
)
def get_default_security_label():
    return default_security_label


# @app.post("/assessments")
def post_assessment(ass: IesAssessment):
    mint_uri(ass)
    state_uri = ""
    start_state = ""
    end_state = ""
    state_type = ""
    if ass.assessedItem is None or ass.assessedItem == "":
        raise HTTPException(status_code=400, detail="No assessed object provided")
    if ass.assessmentType is None or ass.assessmentType == "":
        raise HTTPException(status_code=400, detail="No assessment class provided")
    if ass.assessmentType not in assessment_classes:
        get_assessments()
        if ass.assessmentType not in assessment_classes:
            safe_type = sanitize_for_message(ass.assessmentType)
            raise HTTPException(
                status_code=404,
                detail=f"Assessment Class: {safe_type} not found",
            )
        else:
            if ass.userOverride:
                user = ass.userOverride
            else:
                user = data_uri_stub + "JaneDoe"  # DON'T KNOW HOW TO GET THE USER ID

            start_date = ISO_8601_URL + ass.startDate.isoformat().replace(" ", "T")
            end_date = ISO_8601_URL + ass.endDate.isoformat().replace(" ", "T")
            query = f"""INSERT DATA
            {{
                <{state_uri}> a <{state_type}> .
                <{state_uri}> ies:isStateOf <{ass.assessedItem}>
                <{start_state}> a ies:BoundingState .
                <{start_state}> ies:isStartOf <{state_uri}> .
                <{start_state}> ies:inPeriod <{start_date}> .
                <{end_state}> a ies:BoundingState .
                <{end_state}> ies:isEndOf <{state_uri}> .
                <{end_state}> ies:inPeriod <{end_date}> .
                <{ass.uri}> a <{ass.assessmentType}>  .
                <{ass.uri}> ies:assessed <{state_uri}> .
                <{ass.uri}> ies:assessor <{user}> .
            }}"""
            run_sparql_update(query=query, security_label=ass.securityLabel)

            return ass.uri
    raise HTTPException(status_code=400, detail="Could not create assessment")


@router.get("/user-details")
def get_user_details(request: Request):
    try:
        return access_client.get_user_details(request.headers)
    except exceptions.RequestException as e:
        if e.response is not None:
            raise HTTPException(
                e.response.status_code,
                f"Error calling Access client:{sanitize_for_message(e.response.reason)}",
            )
        else:
            raise HTTPException(codes.internal_server_error, ACCESS_API_CALL_ERROR)


@router.get("/signout-links")
def get_signout_links():
    try:
        signout_links_response = requests.get(
            f"{config_settings.IDENTITY_API_URL}/api/v1/links/sign-out"
        )
        if signout_links_response.status_code == codes.ok:
            return {
                "oauth2SignoutUrl": f"{config_settings.LANDING_PAGE_URL}/oauth2/sign_out",
                "redirectUrl": signout_links_response.json(),
            }
        else:
            reason = sanitize_for_message(signout_links_response.reason)
            return f"Error {signout_links_response.status_code}: {reason}"
    except exceptions.RequestException as e:
        if e.response is not None:
            raise HTTPException(
                e.response.status_code,
                f"Error calling the identity api: {sanitize_for_message(e.response.reason)}",
            )
        else:
            raise HTTPException(codes.internal_server_error, IDENTITY_API_CALL_ERROR)


@router.get(
    "/buildings/{uprn}/wind-driven-rain",
    response_model=BuildingWindDrivenRainData,
    description="returns wind driven rain data for the building that corresponds to the provided UPRN",
    responses={
        404: {"detail": "Unable to find wind driven rain data for the provided UPRN!"}
    },
)
async def get_wind_driven_rain_data_by_uprn(
    uprn: str,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    query, params = get_wind_driven_rain_data_for_building_query(uprn)
    result = await db.execute(text(query), params)

    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to find wind driven rain data for the provided UPRN!",
        )

    row = BuildingWindDrivenRainSchema.from_orm(row)
    return map_building_wind_driven_rain_response(row)


@router.get(
    "/buildings/{uprn}/hot-summer-days",
    response_model=BuildingHotSummerDaysData,
    description="returns hot summer days data for the building that corresponds to the provided UPRN",
    responses={
        404: {
            "description": "Unable to find hot summer days data for the provided UPRN!"
        }
    },
)
async def get_hot_summer_days_data_by_uprn(
    uprn: str,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    query, params = get_hot_summer_days_data_for_building_query(uprn)
    result = await db.execute(text(query), params)

    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to find hot summer days data for the provided UPRN!",
        )

    row = BuildingHotSummerDaysSchema.from_orm(row)
    return map_building_hot_summer_days_response(row)


@router.get(
    "/buildings/{uprn}/icing-days",
    response_model=BuildingIcingDaysData,
    description="returns icing days data for the building that corresponds to the provided UPRN",
    responses={
        404: {"description": "Unable to find icing days data for the provided UPRN!"}
    },
)
async def get_icing_days_data_by_uprn(
    uprn: str,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    query, params = get_icing_days_data_for_building_query(uprn)
    result = await db.execute(text(query), params)

    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to find icing days data for the provided UPRN!",
        )

    row = BuildingIcingDaysSchema.from_orm(row)
    return map_building_icing_days_response(row)


@router.get(
    "/buildings/{uprn}/hours-of-sunlight",
    response_model=BuildingSunlightHoursData,
    description="returns hours of sunlight data for the building that corresponds to the provided UPRN",
    responses={
        404: {
            "description": "Unable to find hours of sunlight data for the provided UPRN!"
        }
    },
)
async def get_sunlight_hours_data_by_uprn(
    uprn: str,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    query, params = get_sunlight_hours_data_for_building_query(uprn)
    result = await db.execute(text(query), params)

    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to find hours of sunlight data for the provided UPRN!",
        )

    row = BuildingSunlightHoursSchema.from_orm(row)
    return map_building_sunlight_hours_response(row)


@router.get(
    "/buildings/{uprn}/weather-summary",
    response_model=BuildingExtremeWeatherSummaryData,
    description="returns weather summary data for the building that corresponds to the provided UPRN",
    responses={
        404: {
            "description": "Unable to find weather summary data for the provided UPRN!"
        }
    },
)
async def get_weather_summary_data_by_uprn(
    uprn: str,
    req: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    query, params = get_weather_summary_data_for_building_query(uprn)
    result = await db.execute(text(query), params)

    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to find weather summary data for the provided UPRN!",
        )

    row = BuildingExtremeWeatherSummarySchema.from_orm(row)
    return map_building_weather_summary_response(row)


@router.get(
    "/data/buildings/download",
    response_model=List[BuildingDetailsForBulkDownload],
    description="returns a list of building details for the provided uprns",
)
async def get_building_details_for_bulk_download(
    uprns: Annotated[List[str], Query()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    query, params = get_building_details_for_bulk_download_query(uprns)
    query_text = text(query)
    query_text = query_text.bindparams(bindparam("uprns", expanding=True))

    results = await db.execute(query_text, params)

    schema_results = [
        BuildingDetailsForBulkDownloadSchema.from_orm(row) for row in results
    ]
    mapped_results = [
        map_building_details_for_bulk_download(result) for result in schema_results
    ]

    return mapped_results
