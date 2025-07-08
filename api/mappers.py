# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import re

from models.dto_models import (
    DetailedBuilding,
    EpcAndOsBuildingSchema,
    EpcStatistics,
    FilterableBuilding,
    FilterableBuildingSchema,
    FilterSummary,
    FlaggedBuilding,
    FlagHistory,
    SimpleBuilding,
)

structure_unit_type_hierarchy = {
    "House": 1,
    "Flat": 1,
    "Park Home": 1,
    "Maisonette": 2,
    "Bungalow": 2,
}
get_type_rank = structure_unit_type_hierarchy.get


def strip_uri(uri: str) -> str:
    """
    Utility method to strip the relevant resource from the URI.

    Args:
        uri (str): The URI from which to extract the resource.

    Returns:
        str: The resource.
    """
    if "http" not in uri:
        # the uri is a literal value
        return uri
    elif "UPRN_" in uri:
        split = uri.split("UPRN_")
    elif "iso8601.iso.org/" in uri:
        split = uri.split("iso8601.iso.org/")
    else:
        split = uri.split("#")
    if len(split) > 1:
        return split[-1]
    else:
        return ""


def get_value_from_result(result: dict, field: str) -> str:
    return strip_uri(get_uri_from_result(result, field))


def get_uri_from_result(result: dict, field: str) -> str:
    if field in result.keys():
        return result[field]["value"]
    else:
        return ""


def get_int_value_from_result(result: dict, field: str) -> int:
    return int(strip_uri(result[field]["value"]))


def map_building_results(building: DetailedBuilding, results: dict) -> None:
    """
    Maps generic building data to a `SingleBuilding` instance.

    Args:
        building (SingleBuilding): A representation of a building.
        results (dict): General SPARQL data retrieved regarding the building e.g. the type of the structure unit.

    Returns:
        None
    """
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            building.lodgement_date = get_value_from_result(result, "lodgementDate")
            building.built_form = get_value_from_result(result, "builtForm")
            building.structure_unit_type = get_value_from_result(
                result, "structureUnitType"
            )


def map_roof_results(building: DetailedBuilding, results: dict) -> None:
    """
    Maps roof-related data to a `SingleBuilding` instance.

    Args:
        building (SingleBuilding): A representation of a building.
        results (dict): Roof-related SPARQL data retrieved regarding the building e.g. the construction of the roof.

    Returns:
        None
    """
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            building.roof_construction = get_value_from_result(
                result, "roofConstruction"
            )
            building.roof_insulation_location = get_value_from_result(
                result, "roofInsulation"
            )
            building.roof_insulation_thickness = get_value_from_result(
                result, "roofInsulationThickness"
            )


def map_floor_results(building: DetailedBuilding, results: dict) -> None:
    """
    Maps floor-related data to a `SingleBuilding` instance.

    Args:
        building (SingleBuilding): A representation of a building.
        results (dict): Floor-related SPARQL data retrieved regarding the building e.g. the construction of the floor.

    Returns:
        None
    """
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            building.floor_construction = get_value_from_result(
                result, "floorConstruction"
            )
            building.floor_insulation = get_value_from_result(result, "floorInsulation")


def map_wall_window_results(building: DetailedBuilding, results: dict) -> None:
    """
    Maps wall and window-related data to a `SingleBuilding` instance.

    Args:
        building (SingleBuilding): A representation of a building.
        results (dict): Wall and window-related SPARQL data retrieved regarding the building e.g. the glazing of the windows.

    Returns:
        None
    """
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            building.wall_construction = get_value_from_result(
                result, "wallConstruction"
            )
            building.wall_insulation = get_value_from_result(result, "wallInsulation")
            building.window_glazing = get_value_from_result(result, "windowGlazing")


def map_single_building_response(
    uprn: str,
    building_results: dict,
    roof_results: dict,
    floor_results: dict,
    wall_window_results: dict,
) -> DetailedBuilding:
    """
    Maps a `DetailedBuilding` response from SPARQL queries for generic, roof, floor, wall and window data.

    Args:
        urpn (str): The UPRN of the building.
        building_results (dict): General SPARQL data retrieved regarding the building e.g. the type of the structure unit.
        roof_results (dict): Roof-related SPARQL data retrieved regarding the building e.g. the construction of the roof.
        floor_results (dict): Floor-related SPARQL data retrieved regarding the building e.g. the construction of the floor.
        wall_window_results (dict): Wall and window-related SPARQL data retrieved regarding the building e.g. the glazing of the windows.

    Returns:
        DetailedBuilding: A detailed representation of a building.
    """
    building = DetailedBuilding()
    building.uprn = uprn
    map_building_results(building, building_results)
    map_roof_results(building, roof_results)
    map_floor_results(building, floor_results)
    map_wall_window_results(building, wall_window_results)
    return building


def map_bounded_buildings_response(
    results: [EpcAndOsBuildingSchema],
) -> list[SimpleBuilding]:
    """
    Maps a `SimpleBuilding` array response from a SQL query result.

    Args:
        results list[BuildingGeoMappingSchema]: General data retrieved regarding the building
        e.g. the UPRN, TOID, coordinates.

    Returns:
        list[SimpleBuilding]: A list of `SimpleBuilding` instances.
    """
    buildings = {}
    if results:
        for result in results:
            # Take the lowest rank of structure unit type, e.g. take "Maisonette" over "Flat"
            if result.uprn not in buildings or get_type_rank(
                result.structure_unit_type, 0
            ) > get_type_rank(buildings[result.uprn].structure_unit_type, 0):
                building = SimpleBuilding()
                building.uprn = result.uprn
                building.first_line_of_address = result.first_line_of_address
                building.toid = result.toid
                building.energy_rating = result.epc_rating
                building.structure_unit_type = result.structure_unit_type
                building.latitude = str(result.lattitude)
                building.longitude = str(result.longitude)
                buildings[result.uprn] = building
    return list(buildings.values())


def map_bounded_filterable_buildings_response(
    results: list[FilterableBuildingSchema],
) -> list[FilterableBuilding]:
    """
    Maps a `FilterableBuildingSchema` array response from a SQL query result.

    Args:
        list[FilterableBuildingSchema]: Detailed SQL data retrieved regarding the building e.g. the UPRN, window glazing, wall construction etc.

    Returns:
        list[FilterableBuilding]: A list of `DetailedBuilding` instances.
    """
    buildings = []
    if results:
        for result in results:
            building = FilterableBuilding()
            building.uprn = result.uprn
            building.lodgement_date = str(result.lodgement_date)
            building.postcode = result.post_code
            building.built_form = result.built_form
            building.fuel_type = result.fuel_type
            building.window_glazing = result.window_glazing
            building.wall_construction = result.wall_construction
            building.wall_insulation = result.wall_insulation
            building.floor_construction = result.floor_construction
            building.floor_insulation = result.floor_insulation
            building.roof_construction = result.roof_construction
            building.roof_insulation_location = result.roof_insulation
            building.roof_insulation_thickness = result.roof_insulation_thickness
            buildings.append(building)
    return buildings


def map_epc_statistics_response(results: dict) -> list[EpcStatistics]:
    """
    Maps a `EpcStatistics` array response from a SPARQL query result.

    Args:
        results (dict): Aggregated statistics for EPC data retrieved via SPARQL query.

    Returns:
        list[EpcStatistics]: A list of `EpcStatistics` instances.
    """
    stats = []
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            stat = EpcStatistics()
            stat.name = get_value_from_result(result, "wardName")
            stat.a_rating = get_int_value_from_result(result, "EPC_Rating_A")
            stat.b_rating = get_int_value_from_result(result, "EPC_Rating_B")
            stat.c_rating = get_int_value_from_result(result, "EPC_Rating_C")
            stat.d_rating = get_int_value_from_result(result, "EPC_Rating_D")
            stat.e_rating = get_int_value_from_result(result, "EPC_Rating_E")
            stat.f_rating = get_int_value_from_result(result, "EPC_Rating_F")
            stat.g_rating = get_int_value_from_result(result, "EPC_Rating_G")
            stat.no_rating = get_int_value_from_result(result, "No_EPC_Rating")
            stats.append(stat)
    return stats


def map_structure_unit_flag_history_response(results: dict) -> list[FlagHistory]:
    """
    Maps a `FlagHistory` array response from a SPARQL query result.

    Args:
        results (dict): A list of flags which have been raised against a structure unit.

    Returns:
        list[FlagHistory]: A list of `FlagHistory` instances.
    """
    flags = []
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            flag = FlagHistory()
            flag.uprn = get_value_from_result(result, "uprn")
            flag.flagged = get_uri_from_result(result, "flag")
            flag.flag_type = get_value_from_result(result, "flagType")
            flag.flagged_by_name = get_value_from_result(result, "retrofitterName")
            flag.flag_date = get_value_from_result(result, "flagDate")
            flag.assessment_date = get_value_from_result(result, "assessmentDate")
            flag.assessor_name = get_value_from_result(result, "assessorName")
            flag.assessment_reason = get_value_from_result(result, "assessmentReason")
            flags.append(flag)
    return flags


def map_flagged_buildings_response(results: dict) -> list[FlaggedBuilding]:
    """
    Maps a `FlaggedBuilding` array response from a SPARQL query result.

    Args:
        results (dict): A list of buildings which have flags.

    Returns:
        list[FlaggedBuilding]: A list of `FlaggedBuilding` instances.
    """
    flags = []
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            flag = FlaggedBuilding()
            flag.uprn = get_value_from_result(result, "uprn")
            flag.toid = get_value_from_result(result, "toid")
            flag.flagged = get_uri_from_result(result, "flag")
            flags.append(flag)
    return flags


def map_filter_summary_response(results: [FilterableBuildingSchema]) -> FilterSummary:
    """
    Maps a `list[FilterableBuildingSchema]` to a `FilterSummary`

    Args:
        results -> `list[FilterSummarySchema]`: A list of filter summaries for the buildings

    Returns:
        `FilterSummary`: A summary of the available filters
    """
    mapped_result: FilterSummary = FilterSummary()
    for result in results:
        post_code_matches = re.search(r"^[0-9A-Z]{3,4}", result.post_code)
        if post_code_matches:
            transformed_post_code = post_code_matches.group()
            mapped_result.postcode.add(transformed_post_code)
        if result.built_form and len(result.built_form) > 0:
            mapped_result.built_form.add(result.built_form)
        if result.lodgement_date:
            inspection_year = str(result.lodgement_date.year)
            mapped_result.inspection_year.add(inspection_year)
        if result.fuel_type and len(result.fuel_type) > 0:
            mapped_result.fuel_type.add(result.fuel_type)
        if result.window_glazing and len(result.window_glazing) > 0:
            mapped_result.window_glazing.add(result.window_glazing)
        if result.wall_construction and len(result.wall_construction) > 0:
            mapped_result.wall_construction.add(result.wall_construction)
        if result.wall_insulation and len(result.wall_insulation) > 0:
            mapped_result.wall_insulation.add(result.wall_insulation)
        if result.floor_construction and len(result.floor_construction) > 0:
            mapped_result.floor_construction.add(result.floor_construction)
        if result.floor_insulation and len(result.floor_insulation) > 0:
            mapped_result.floor_insulation.add(result.floor_insulation)
        if result.roof_construction and len(result.roof_construction) > 0:
            mapped_result.roof_construction.add(result.roof_construction)
        if result.roof_insulation and len(result.roof_insulation) > 0:
            mapped_result.roof_insulation_location.add(result.roof_insulation)
        if (
            result.roof_insulation_thickness
            and len(result.roof_insulation_thickness) > 0
        ):
            mapped_result.roof_insulation_thickness.add(
                result.roof_insulation_thickness
            )
    return mapped_result
