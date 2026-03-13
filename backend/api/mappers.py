# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import datetime
import re

from models.dto_models import (
    BuildingAttributePercentage,
    BuildingAttributePercentagesPerRegion,
    BuildingDetailsForBulkDownload,
    BuildingDetailsForBulkDownloadSchema,
    BuildingExtremeWeatherSummaryData,
    BuildingExtremeWeatherSummarySchema,
    BuildingHotSummerDaysData,
    BuildingHotSummerDaysSchema,
    BuildingIcingDaysData,
    BuildingIcingDaysSchema,
    BuildingSunlightHoursData,
    BuildingSunlightHoursSchema,
    BuildingWindDrivenRainData,
    BuildingWindDrivenRainSchema,
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


def map_fueltype_results(building: DetailedBuilding, results: dict) -> None:
    """
    Maps fuel type data to a `SingleBuilding` instance.

    Args:
        building (SingleBuilding): A representation of a building.
        results (dict): Fuel type SPARQL data retrieved regarding the building e.g. the glazing of the windows.

    Returns:
        None
    """
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            building.fueltype = get_value_from_result(result, "fuelType")


def map_ngd_roof_material_results(building: DetailedBuilding, results: dict) -> None:

    if (
        results and results.get("results") and results["results"].get("bindings")
    ):  # check if results come from Fuseki or from PostGIS
        for result in results["results"]["bindings"]:
            building.roof_material = get_value_from_result(result, "roofMaterial")
    else:
        if "roof_material" in results.keys():
            building.roof_material = (
                results["roof_material"].replace(" ", "")
                if results["roof_material"]
                else results["roof_material"]
            )


def map_ngd_solar_panel_presence_results(
    building: DetailedBuilding, results: dict
) -> None:
    if results and results.get("results") and results["results"].get("bindings"):
        for result in results["results"]["bindings"]:
            building.solar_panel_presence = get_value_from_result(
                result, "solarPanelPresence"
            )
    else:
        if "solar_panel_presence" in results.keys():
            building.solar_panel_presence = (
                "HasSolarPanels"
                if results["solar_panel_presence"] == "True"
                else "NoSolarPanels"
            )


def map_ngd_roof_shape_results(building: DetailedBuilding, results: dict) -> None:
    if results and results.get("results") and results["results"].get("bindings"):
        for result in results["results"]["bindings"]:
            building.roof_shape = get_value_from_result(result, "roofShape")
    else:
        sag_alignment = {
            "Pitched": "PitchedRoofShape",
            "Flat": "FlatRoofShape",
            "Mixed": "MixedRoofShape",
            "Unknown": "UnknownRoofShape",
            None: None,
        }
        if "roof_shape" in results.keys():
            building.roof_shape = sag_alignment[results["roof_shape"]]


def map_ngd_roof_aspect_area_facings_results(
    building: DetailedBuilding, results: dict
) -> None:
    direction_to_field = {
        "NorthFacingRoofSectionSum": "roof_aspect_area_facing_north_m2",
        "NorthEastFacingRoofSectionSum": "roof_aspect_area_facing_north_east_m2",
        "EastFacingRoofSectionSum": "roof_aspect_area_facing_east_m2",
        "SouthEastFacingRoofSectionSum": "roof_aspect_area_facing_south_east_m2",
        "SouthFacingRoofSectionSum": "roof_aspect_area_facing_south_m2",
        "SouthWestFacingRoofSectionSum": "roof_aspect_area_facing_south_west_m2",
        "WestFacingRoofSectionSum": "roof_aspect_area_facing_west_m2",
        "NorthWestFacingRoofSectionSum": "roof_aspect_area_facing_north_west_m2",
        "AreaIndeterminableRoofSectionSum": "roof_aspect_area_indeterminable_m2",
    }

    def assign(field: str | None, m2) -> None:
        if field and m2 is not None:
            setattr(building, field, float(m2))

    if results and results.get("results") and results["results"].get("bindings"):
        for result in results["results"]["bindings"]:
            assign(
                direction_to_field.get(get_value_from_result(result, "direction")),
                get_value_from_result(result, "m2"),
            )
        return

    if "roof_aspect_area_facing_north_m2" in results:
        for field, m2 in results.items():
            assign(field, m2)


def map_single_building_response(
    uprn: str,
    building_results: dict,
    roof_results: dict,
    floor_results: dict,
    wall_window_results: dict,
    fueltype_results: dict,
    ngd_roof_material_results: dict | None = None,
    ngd_solar_panel_presence_results: dict | None = None,
    ngd_roof_shape_results: dict | None = None,
    ngd_roof_aspect_area_facings_results: dict | None = None,
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
    map_fueltype_results(building, fueltype_results)

    # check if roof material exists
    map_ngd_roof_material_results(building, ngd_roof_material_results)
    map_ngd_solar_panel_presence_results(building, ngd_solar_panel_presence_results)
    map_ngd_roof_shape_results(building, ngd_roof_shape_results)
    map_ngd_roof_aspect_area_facings_results(
        building, ngd_roof_aspect_area_facings_results
    )

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
            building.roof_material = (
                result.roof_material.replace(" ", "")
                if result.roof_material
                else result.roof_material
            )
            building.has_roof_solar_panels = result.has_roof_solar_panels
            building.roof_aspect_area_facing_north = (
                result.roof_aspect_area_facing_north_m2
            )
            building.roof_aspect_area_facing_north_east = (
                result.roof_aspect_area_facing_north_east_m2
            )
            building.roof_aspect_area_facing_north_west = (
                result.roof_aspect_area_facing_north_west_m2
            )
            building.roof_aspect_area_facing_east = (
                result.roof_aspect_area_facing_east_m2
            )
            building.roof_aspect_area_facing_south = (
                result.roof_aspect_area_facing_south_m2
            )
            building.roof_aspect_area_facing_south_east = (
                result.roof_aspect_area_facing_south_east_m2
            )
            building.roof_aspect_area_facing_south_west = (
                result.roof_aspect_area_facing_south_west_m2
            )
            building.roof_aspect_area_facing_west = (
                result.roof_aspect_area_facing_west_m2
            )
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


def _add_postcode_filter(filter_summary: FilterSummary, post_code: str):
    post_code_matches = re.search(r"^[0-9A-Z]{3,4}", post_code)
    if post_code_matches:
        transformed_post_code = post_code_matches.group()
        filter_summary.postcode.add(transformed_post_code)


def _add_built_form_filter(filter_summary: FilterSummary, built_form: str):
    if built_form and len(built_form) > 0:
        filter_summary.built_form.add(built_form)


def _add_lodgment_date_filter(
    filter_summary: FilterSummary, lodgement_date: datetime.date
):
    if lodgement_date:
        inspection_year = str(lodgement_date.year)
        filter_summary.inspection_year.add(inspection_year)


def _add_fuel_type_filter(filter_summary: FilterSummary, fuel_type: str):
    if fuel_type and len(fuel_type) > 0:
        filter_summary.fuel_type.add(fuel_type)


def _add_window_glazing_filter(filter_summary: FilterSummary, window_glazing: str):
    if window_glazing and len(window_glazing) > 0:
        filter_summary.window_glazing.add(window_glazing)


def _add_wall_construction_filter(
    filter_summary: FilterSummary, wall_construction: str
):
    if wall_construction and len(wall_construction) > 0:
        filter_summary.wall_construction.add(wall_construction)


def _add_wall_insulation_filter(filter_summary: FilterSummary, wall_insulation: str):
    if wall_insulation and len(wall_insulation) > 0:
        filter_summary.wall_insulation.add(wall_insulation)


def _add_floor_construction_filter(
    filter_summary: FilterSummary, floor_construction: str
):
    if floor_construction and len(floor_construction) > 0:
        filter_summary.floor_construction.add(floor_construction)


def _add_floor_insulation_filter(filter_summary: FilterSummary, floor_insulation: str):
    if floor_insulation and len(floor_insulation) > 0:
        filter_summary.floor_insulation.add(floor_insulation)


def _add_roof_construction_filter(
    filter_summary: FilterSummary, roof_construction: str
):
    if roof_construction and len(roof_construction) > 0:
        filter_summary.roof_construction.add(roof_construction)


def _add_roof_insulation_location_filter(
    filter_summary: FilterSummary, roof_insulation_location: str
):
    if roof_insulation_location and len(roof_insulation_location) > 0:
        filter_summary.roof_insulation_location.add(roof_insulation_location)


def _add_roof_insulation_thickness_filter(
    filter_summary: FilterSummary, roof_insulation_thickness: str
):
    if roof_insulation_thickness and len(roof_insulation_thickness) > 0:
        filter_summary.roof_insulation_thickness.add(roof_insulation_thickness)


def _add_has_roof_solar_panels_filter(
    filter_summary: FilterSummary, has_roof_solar_panels: bool
):
    if (
        has_roof_solar_panels is not None
        and len(filter_summary.has_roof_solar_panels) < 2
    ):
        filter_summary.has_roof_solar_panels.add(
            "HasSolarPanels" if has_roof_solar_panels else "NoSolarPanels"
        )


def _add_roof_material_filter(filter_summary: FilterSummary, roof_material: str):
    if roof_material and len(roof_material) > 0:
        filter_summary.roof_material.add(roof_material.replace(" ", ""))


def _add_roof_aspect_area_direction_filter(
    filter_summary: FilterSummary,
    roof_aspect_area_facing_north_m2: float,
    roof_aspect_area_facing_north_east_m2: float,
    roof_aspect_area_facing_east_m2: float,
    roof_aspect_area_facing_south_east_m2: float,
    roof_aspect_area_facing_south_m2: float,
    roof_aspect_area_facing_south_west_m2: float,
    roof_aspect_area_facing_west_m2: float,
    roof_aspect_area_facing_north_west_m2: float,
):
    direction_areas = (
        ("North", roof_aspect_area_facing_north_m2),
        ("NorthEast", roof_aspect_area_facing_north_east_m2),
        ("NorthWest", roof_aspect_area_facing_north_west_m2),
        ("South", roof_aspect_area_facing_south_m2),
        ("SouthEast", roof_aspect_area_facing_south_east_m2),
        ("SouthWest", roof_aspect_area_facing_south_west_m2),
        ("East", roof_aspect_area_facing_east_m2),
        ("West", roof_aspect_area_facing_west_m2),
    )
    for direction, area in direction_areas:
        if area and area > 0:
            filter_summary.roof_aspect_area_direction.add(direction)


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
        _add_postcode_filter(mapped_result, result.post_code)
        _add_built_form_filter(mapped_result, result.built_form)
        _add_lodgment_date_filter(mapped_result, result.lodgement_date)
        _add_fuel_type_filter(mapped_result, result.fuel_type)
        _add_window_glazing_filter(mapped_result, result.window_glazing)
        _add_wall_construction_filter(mapped_result, result.wall_construction)
        _add_wall_insulation_filter(mapped_result, result.wall_insulation)
        _add_floor_construction_filter(mapped_result, result.floor_construction)
        _add_floor_insulation_filter(mapped_result, result.floor_insulation)
        _add_has_roof_solar_panels_filter(mapped_result, result.has_roof_solar_panels)
        _add_roof_material_filter(mapped_result, result.roof_material)
        _add_roof_aspect_area_direction_filter(
            mapped_result,
            result.roof_aspect_area_facing_north_m2,
            result.roof_aspect_area_facing_north_east_m2,
            result.roof_aspect_area_facing_east_m2,
            result.roof_aspect_area_facing_south_east_m2,
            result.roof_aspect_area_facing_south_m2,
            result.roof_aspect_area_facing_south_west_m2,
            result.roof_aspect_area_facing_west_m2,
            result.roof_aspect_area_facing_north_west_m2,
        )
        _add_roof_construction_filter(mapped_result, result.roof_construction)
        _add_roof_insulation_location_filter(mapped_result, result.roof_insulation)
        _add_roof_insulation_thickness_filter(
            mapped_result, result.roof_insulation_thickness
        )
    return mapped_result


def map_percentage_building_attributes_per_region_response(
    results,
) -> list[BuildingAttributePercentagesPerRegion]:
    attribute_mappings = [
        ("percentage_single_glazing", "Single glazing"),
        ("percentage_double_glazing", "Double glazing"),
        ("percentage_triple_glazing", "Triple glazing"),
        ("percentage_no_insulation", "No insulation"),
        ("percentage_insulation_1_100mm", "1-100mm insulation"),
        ("percentage_insulation_101_200mm", "101-200mm insulation"),
        ("percentage_insulation_201_300mm", "201-300mm insulation"),
        ("percentage_insulation_over_300mm", ">300mm insulation"),
        ("percentage_suspended_flooring", "Suspended flooring"),
        ("percentage_pitched_roof", "Pitched roofs"),
        ("percentage_cavity_wall", "Cavity walls"),
        ("percentage_roof_solar_panels", "Solar panels"),
    ]

    mapped_results = []
    for row in results:
        attributes = []
        for column_name, label in attribute_mappings:
            value = getattr(row, column_name, 0.0)
            attributes.append(
                BuildingAttributePercentage(label=label, value=float(value))
            )

        mapped_results.append(
            BuildingAttributePercentagesPerRegion(
                region_name=row.region_name, attributes=attributes
            )
        )

    return mapped_results


def map_building_wind_driven_rain_response(
    row: BuildingWindDrivenRainSchema,
) -> BuildingWindDrivenRainData:
    data = BuildingWindDrivenRainData(
        north_two_degrees_median=row.wdr20_0,
        north_east_two_degrees_median=row.wdr20_45,
        east_two_degrees_median=row.wdr20_90,
        south_east_two_degrees_median=row.wdr20_135,
        south_two_degrees_median=row.wdr20_180,
        south_west_two_degrees_median=row.wdr20_225,
        west_two_degrees_median=row.wdr20_270,
        north_west_two_degrees_median=row.wdr20_315,
        north_four_degrees_median=row.wdr40_0,
        north_east_four_degrees_median=row.wdr40_45,
        east_four_degrees_median=row.wdr40_90,
        south_east_four_degrees_median=row.wdr40_135,
        south_four_degrees_median=row.wdr40_180,
        south_west_four_degrees_median=row.wdr40_225,
        west_four_degrees_median=row.wdr40_270,
        north_west_four_degrees_median=row.wdr40_315,
    )

    return data


def map_building_hot_summer_days_response(
    row: BuildingHotSummerDaysSchema,
) -> BuildingHotSummerDaysData:
    data = BuildingHotSummerDaysData(
        hsd_baseline=row.hsd_baseline_01_20_median,
        hsd_1_5_degree_above_baseline=row.hsd_15_median,
        hsd_2_0_degree_above_baseline=row.hsd_20_median,
        hsd_2_5_degree_above_baseline=row.hsd_25_median,
        hsd_3_0_degree_above_baseline=row.hsd_30_median,
        hsd_4_0_degree_above_baseline=row.hsd_40_median,
    )

    return data


def map_building_icing_days_response(row: BuildingIcingDaysSchema):
    data = BuildingIcingDaysData(icing_days=row.icingdays)

    return data


def map_building_sunlight_hours_response(row: BuildingSunlightHoursSchema):
    data = BuildingSunlightHoursData(
        sunlight_hours=row.sunlight_hours, daily_sunlight_hours=row.daily_sunlight_hours
    )

    return data


def map_building_weather_summary_response(row: BuildingExtremeWeatherSummarySchema):
    data = BuildingExtremeWeatherSummaryData(
        affected_by_icing_days=(
            row.affected_by_icing_days
            if row.affected_by_icing_days is not None
            else False
        ),
        affected_by_hot_summer_days=(
            row.affected_by_hsds if row.affected_by_hsds is not None else False
        ),
        affected_by_wind_driven_rain=(
            row.affected_by_wdr if row.affected_by_wdr is not None else False
        ),
    )

    return data


def map_building_details_for_bulk_download(row: BuildingDetailsForBulkDownloadSchema):
    data = BuildingDetailsForBulkDownload(
        uprn=row.uprn,
        longitude=row.longitude,
        latitude=row.lattitude,
        first_line_of_address=row.first_line_of_address,
        post_code=row.post_code,
        energy_rating=row.epc_rating,
        sap_rating=row.sap_rating,
        toid=row.toid,
        lodgement_date=row.lodgement_date,
        built_form=row.built_form,
        floor_construction=row.floor_construction,
        floor_insulation=row.floor_insulation,
        roof_construction=row.roof_construction,
        roof_insulation_location=row.roof_insulation,
        roof_insulation_thickness=row.roof_insulation_thickness,
        wall_construction=row.wall_construction,
        wall_insulation=row.wall_insulation,
        window_glazing=row.window_glazing,
        fueltype=row.fuel_type,
        roof_material=row.roof_material,
        solar_panel_presence=row.solar_panel_presence,
        roof_shape=row.roof_shape,
        roof_aspect_area_facing_north_m2=row.roof_aspect_area_facing_north_m2,
        roof_aspect_area_facing_north_east_m2=row.roof_aspect_area_facing_north_east_m2,
        roof_aspect_area_facing_east_m2=row.roof_aspect_area_facing_east_m2,
        roof_aspect_area_facing_south_east_m2=row.roof_aspect_area_facing_south_east_m2,
        roof_aspect_area_facing_south_m2=row.roof_aspect_area_facing_south_m2,
        roof_aspect_area_facing_south_west_m2=row.roof_aspect_area_facing_south_west_m2,
        roof_aspect_area_facing_west_m2=row.roof_aspect_area_facing_west_m2,
        roof_aspect_area_facing_north_west_m2=row.roof_aspect_area_facing_north_west_m2,
        roof_aspect_area_indeterminable_m2=row.roof_aspect_area_indeterminable_m2,
        north_two_degrees_median=row.wdr20_0,
        north_east_two_degrees_median=row.wdr20_45,
        east_two_degrees_median=row.wdr20_90,
        south_east_two_degrees_median=row.wdr20_135,
        south_two_degrees_median=row.wdr20_180,
        south_west_two_degrees_median=row.wdr20_225,
        west_two_degrees_median=row.wdr20_270,
        north_west_two_degrees_median=row.wdr20_315,
        north_four_degrees_median=row.wdr40_0,
        north_east_four_degrees_median=row.wdr40_45,
        east_four_degrees_median=row.wdr40_90,
        south_east_four_degrees_median=row.wdr40_135,
        south_four_degrees_median=row.wdr40_180,
        south_west_four_degrees_median=row.wdr40_225,
        west_four_degrees_median=row.wdr40_270,
        north_west_four_degrees_median=row.wdr40_315,
        hsd_baseline=row.hsd_baseline_01_20_median,
        hsd_1_5_degree_above_baseline=row.hsd_15_median,
        hsd_2_0_degree_above_baseline=row.hsd_20_median,
        hsd_2_5_degree_above_baseline=row.hsd_25_median,
        hsd_3_0_degree_above_baseline=row.hsd_30_median,
        hsd_4_0_degree_above_baseline=row.hsd_40_median,
        icing_days=row.icingdays,
        sunlight_hours=row.sunlight_hours,
        daily_sunlight_hours=row.daily_sunlight_hours,
    )

    return data
