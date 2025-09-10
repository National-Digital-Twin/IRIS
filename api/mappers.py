# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import datetime
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
    if results and results.get("results") and results["results"].get("bindings"):
        for result in results["results"]["bindings"]:
            building.roof_material = get_value_from_result(result, "roofMaterial")


def map_ngd_solar_panel_presence_results(
    building: DetailedBuilding, results: dict
) -> None:
    if results and results.get("results") and results["results"].get("bindings"):
        for result in results["results"]["bindings"]:
            building.solar_panel_presence = get_value_from_result(
                result, "solarPanelPresence"
            )


def map_ngd_roof_shape_results(building: DetailedBuilding, results: dict) -> None:
    if results and results.get("results") and results["results"].get("bindings"):
        for result in results["results"]["bindings"]:
            building.roof_shape = get_value_from_result(result, "roofShape")


def map_ngd_roof_aspect_area_facings_results(
    building: DetailedBuilding, results: dict
) -> None:
    direction_to_field = {
        "NorthFacingRoofSectionSum": "roof_aspect_area_facing_north",
        "NorthEastFacingRoofSectionSum": "roof_aspect_area_facing_northeast",
        "EastFacingRoofSectionSum": "roof_aspect_area_facing_east",
        "SouthEastFacingRoofSectionSum": "roof_aspect_area_facing_southeast",
        "SouthFacingRoofSectionSum": "roof_aspect_area_facing_south",
        "SouthWestFacingRoofSectionSum": "roof_aspect_area_facing_southwest",
        "WestFacingRoofSectionSum": "roof_aspect_area_facing_west",
        "NorthWestFacingRoofSectionSum": "roof_aspect_area_facing_northwest",
        "AreaIndeterminableRoofSectionSum": "roof_aspect_area_facing_indeterminable",
    }
    if results and results.get("results") and results["results"].get("bindings"):
        for result in results["results"]["bindings"]:
            direction = get_value_from_result(result, "direction")
            m2 = get_value_from_result(result, "m2")
            field = direction_to_field.get(direction)
            if field:
                setattr(building, field, m2)


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
    if ngd_roof_material_results is not None:
        map_ngd_roof_material_results(building, ngd_roof_material_results)
    if ngd_solar_panel_presence_results is not None:
        map_ngd_solar_panel_presence_results(building, ngd_solar_panel_presence_results)
    if ngd_roof_shape_results is not None:
        map_ngd_roof_shape_results(building, ngd_roof_shape_results)
    if ngd_roof_aspect_area_facings_results is not None:
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
    if (
        roof_aspect_area_facing_north_m2
        and roof_aspect_area_facing_north_m2 > 0
        and "North" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("North")
    if (
        roof_aspect_area_facing_north_east_m2
        and roof_aspect_area_facing_north_east_m2 > 0
        and "NorthEast" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("NorthEast")
    if (
        roof_aspect_area_facing_north_west_m2
        and roof_aspect_area_facing_north_west_m2 > 0
        and "NorthWest" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("NorthWest")
    if (
        roof_aspect_area_facing_south_m2
        and roof_aspect_area_facing_south_m2 > 0
        and "South" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("South")
    if (
        roof_aspect_area_facing_south_east_m2
        and roof_aspect_area_facing_south_east_m2 > 0
        and "SouthEast" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("SouthEast")
    if (
        roof_aspect_area_facing_south_west_m2
        and roof_aspect_area_facing_south_west_m2 > 0
        and "SouthWest" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("SouthWest")
    if (
        roof_aspect_area_facing_east_m2
        and roof_aspect_area_facing_east_m2 > 0
        and "East" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("East")
    if (
        roof_aspect_area_facing_west_m2
        and roof_aspect_area_facing_west_m2 > 0
        and "West" not in filter_summary.roof_aspect_area_direction
    ):
        filter_summary.roof_aspect_area_direction.add("West")


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
