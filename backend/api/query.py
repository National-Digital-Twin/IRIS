# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from utils import expand_wales_region, WELSH_REGIONS

EPC_ACTIVE_TRUE = "epc_active = true"
WELSH_REGIONS_SQL = ", ".join(f"'{region}'" for region in sorted(WELSH_REGIONS))


def get_building(uprn: str) -> str:
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ies: <http://informationexchangestandard.org/ont/ies#>
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data: <http://ndtp.co.uk/data#>

        SELECT ?lodgementDate ?builtForm ?structureUnitType WHERE {{
            ?structureUnit ies:isIdentifiedBy data:UPRN_{uprn} .
            ?structureUnit a building:StructureUnit .
            ?structureUnitState a building:StructureUnitState .
            ?structureUnitState ies:isStateOf ?structureUnit .

            ?epc_result building:lodgementDate ?lodgementDate .
            ?epc_result ies:isParticipantIn ?epc_assessment .
            ?epc_assessment building:assessedStateForEnergyPerformance ?structureUnitState .

            OPTIONAL {{
                ?addressMatch a ies:AssessToBeTrue ;
                    ies:assessed data:UPRN_{uprn} ;
                    ies:confidence ?matchScore ;
                    ies:isPartOf ?epc_assessment .
            }}

            OPTIONAL {{
                ?_bf a ?builtForm .
                ?builtForm a building:BuiltForm .
                ?_bf ies:isStateOf ?structureUnit .
            }}

            OPTIONAL {{
                ?_sut a ?structureUnitType .
                ?structureUnitType a building:StructureUnitType .
                ?_sut ies:isStateOf ?structureUnit .
            }}
        }} ORDER BY ASC(BOUND(?matchScore)) DESC(?matchScore) DESC(?lodgementDate)
        LIMIT 1
    """


def get_roof_for_building(uprn: str) -> str:
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ies: <http://informationexchangestandard.org/ont/ies#>
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data: <http://ndtp.co.uk/data#>

        SELECT ?uprn ?roofConstruction ?roofInsulation ?roofInsulationThickness
        WHERE {{
            ?structureUnit ies:isIdentifiedBy data:UPRN_{uprn} .
            ?structureUnit a building:StructureUnit .
            ?structureUnitState a building:StructureUnitState .
            ?structureUnitState ies:isStateOf ?structureUnit .

            ?epc_result building:lodgementDate ?lodgementDate .
            ?epc_result ies:isParticipantIn ?epc_assessment .
            ?epc_assessment building:assessedStateForEnergyPerformance ?structureUnitState .

            OPTIONAL {{
                ?addressMatch a ies:AssessToBeTrue ;
                    ies:assessed data:UPRN_{uprn} ;
                    ies:confidence ?matchScore ;
                    ies:isPartOf ?epc_assessment .
            }}

            OPTIONAL {{
                ?_rc a ?roofConstruction .
                ?roofConstruction a building:RoofConstruction .
                ?_rc ies:isPartOf ?structureUnitState .
            }}

            OPTIONAL {{
                ?_ri a ?roofInsulation .
                ?roofInsulation a building:RoofInsulationLocation .
                ?_ri ies:isPartOf ?structureUnitState .
            }}

            OPTIONAL {{
                ?_rit a ?roofInsulationThickness .
                ?roofInsulationThickness a building:RoofInsulationThickness .
                ?_rit ies:isPartOf ?structureUnitState .
            }}
        }} ORDER BY ASC(BOUND(?matchScore)) DESC(?matchScore) DESC(?lodgementDate)
        LIMIT 1
    """


def get_floor_for_building(uprn: str) -> str:
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ies: <http://informationexchangestandard.org/ont/ies#>
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data: <http://ndtp.co.uk/data#>

        SELECT ?uprn ?floorConstruction ?floorInsulation WHERE {{

        ?structureUnit ies:isIdentifiedBy data:UPRN_{uprn} .
        ?structureUnit a building:StructureUnit .
        ?structureUnitState a building:StructureUnitState .
        ?structureUnitState ies:isStateOf ?structureUnit .

        ?epc_result building:lodgementDate ?lodgementDate .
        ?epc_result ies:isParticipantIn ?epc_assessment .
        ?epc_assessment building:assessedStateForEnergyPerformance ?structureUnitState .

        OPTIONAL {{
            ?addressMatch a ies:AssessToBeTrue ;
                ies:assessed data:UPRN_{uprn} ;
                ies:confidence ?matchScore ;
                ies:isPartOf ?epc_assessment .
        }}

        OPTIONAL {{
            ?_fc a ?floorConstruction .
            ?floorConstruction a building:FloorConstruction .
            ?_fc ies:isPartOf ?structureUnitState .
        }}

        OPTIONAL {{
            ?_fi a ?floorInsulation .
            ?floorInsulation a building:FloorInsulation .
            ?_fi ies:isPartOf ?structureUnitState .
        }}

        }} ORDER BY ASC(BOUND(?matchScore)) DESC(?matchScore) DESC(?lodgementDate)
        LIMIT 1
    """


def get_walls_and_windows_for_building(uprn: str) -> str:
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ies: <http://informationexchangestandard.org/ont/ies#>
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data: <http://ndtp.co.uk/data#>

        SELECT ?uprn ?wallConstruction ?wallInsulation ?windowGlazing WHERE {{

            ?structureUnit ies:isIdentifiedBy data:UPRN_{uprn} .
            ?structureUnit a building:StructureUnit .
            ?structureUnitState a building:StructureUnitState .
            ?structureUnitState ies:isStateOf ?structureUnit .

            ?epc_result building:lodgementDate ?lodgementDate .
            ?epc_result ies:isParticipantIn ?epc_assessment .
            ?epc_assessment building:assessedStateForEnergyPerformance ?structureUnitState .

            OPTIONAL {{
                ?addressMatch a ies:AssessToBeTrue ;
                    ies:assessed data:UPRN_{uprn} ;
                    ies:confidence ?matchScore ;
                    ies:isPartOf ?epc_assessment .
            }}

            OPTIONAL {{
                ?_wc a ?wallConstruction .
                ?wallConstruction a building:WallConstruction .
                ?_wc ies:isPartOf ?structureUnitState .
            }}

            OPTIONAL {{
                ?_wi a ?wallInsulation .
                ?wallInsulation a building:WallInsulation .
                ?_wi ies:isPartOf ?structureUnitState .
            }}

            OPTIONAL {{
                ?_wg a ?windowGlazing .
                ?windowGlazing a building:GlazingType .
                ?_wg ies:isPartOf ?structureUnitState .
            }}

        }} ORDER BY ASC(BOUND(?matchScore)) DESC(?matchScore) DESC(?lodgementDate)
        LIMIT 1
    """


def get_fueltype_for_building(uprn: str) -> str:
    return f"""
        PREFIX ies:      <http://informationexchangestandard.org/ont/ies#>
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data:     <http://ndtp.co.uk/data#>
        PREFIX xsd:      <http://www.w3.org/2001/XMLSchema#>

        SELECT ?fuelType
            WHERE {{
            {{
                SELECT ?structureUnit ?structureUnitState ?lodgement
                WHERE {{
                        ?structureUnit ies:isIdentifiedBy data:UPRN_{uprn} ;
                                        a building:StructureUnit .
                        ?structureUnitState a building:StructureUnitState ;
                                ies:isStateOf ?structureUnit .
                        ?epc_assessment building:assessedStateForEnergyPerformance ?structureUnitState .
                        
                        OPTIONAL {{
                            ?addressMatch a ies:AssessToBeTrue ;
                                ies:assessed data:UPRN_{uprn} ;
                                ies:confidence ?matchScore ;
                                ies:isPartOf ?epc_assessment .
                        }}
                                
                        BIND(STR(?structureUnitState) AS ?s)            # cast structure unit state URI to a string
                        BIND(REPLACE(?s, ".*_([0-9]{{8}})$", "$1") AS ?yyyymmdd)    # get last 8 digits

                        # check if we managed to pull the last 8 digits if the regex pattern matched
                        FILTER( ?yyyymmdd != ?s )

                        # split into year, month and day components
                        BIND(SUBSTR(?yyyymmdd,1,4) AS ?yyyy)
                        BIND(SUBSTR(?yyyymmdd,5,2) AS ?mm)
                        BIND(SUBSTR(?yyyymmdd,7,2) AS ?dd)

                        # check whether month and day are within expected intervals
                        FILTER ( xsd:integer(?mm) >= 1 && xsd:integer(?mm) <= 12 )
                        FILTER ( xsd:integer(?dd) >= 1 && xsd:integer(?dd) <= 31 )

                        # create the final date component
                        BIND( xsd:date(CONCAT(?yyyy, "-", ?mm, "-", ?dd)) AS ?lodgement )
                    }} ORDER BY ASC(BOUND(?matchScore)) DESC(?matchScore) DESC(?lodgement) LIMIT 1
            }}
                GRAPH <http://ndtp.com/graph/heating-v2> {{
                        ?structureUnitState building:isServicedBy ?heatingSystem .
                        ?heatingSystem building:isOperableWithFuel ?fuelType .
            }}
        }}
    """

def get_epc_attributes_pg() -> str:
    return """
        WITH selected_dwelling AS (
            SELECT uprn, toid, post_code, point
            FROM iris.building
            WHERE is_residential = true
                AND uprn = :uprn
        )
        SELECT
            sd.uprn, sd.toid, sd.post_code,
            su.built_form, 
            su.type as structure_unit_type,
            su.fuel_type,
            ea.lodgement_date, su.window_glazing,
            su.wall_construction, su.wall_insulation,
            su.floor_construction, su.floor_insulation,
            su.roof_construction, 
            su.roof_insulation as roof_insulation_location,
            su.roof_insulation_thickness
        FROM
            selected_dwelling sd
        LEFT JOIN LATERAL (
            SELECT
                id,
                uprn,
                epc_rating,
                lodgement_date
            FROM
                iris.epc_assessment
            WHERE
                uprn = sd.uprn
            ORDER BY
                match_score desc nulls first,
                lodgement_date desc nulls last,
                id desc
            LIMIT 1
        ) ea ON TRUE
        LEFT JOIN iris.structure_unit su
        ON
            su.epc_assessment_id = ea.id;
    """

def get_all_ngd_attributes_pg() -> str:
    return """
        SELECT
            su.has_roof_solar_panels,
            su.roof_material,
            su.roof_shape,
            su.roof_aspect_area_facing_north_m2,
            su.roof_aspect_area_facing_north_east_m2,
            su.roof_aspect_area_facing_east_m2,
            su.roof_aspect_area_facing_south_east_m2,
            su.roof_aspect_area_facing_south_m2,
            su.roof_aspect_area_facing_south_west_m2,
            su.roof_aspect_area_facing_west_m2,
            su.roof_aspect_area_facing_north_west_m2,
            su.roof_aspect_area_indeterminable_m2
        FROM iris.structure_unit su
        WHERE su.uprn = :uprn
        UNION
        SELECT
            su.has_roof_solar_panels,
            su.roof_material,
            su.roof_shape,
            su.roof_aspect_area_facing_north_m2,
            su.roof_aspect_area_facing_north_east_m2,
            su.roof_aspect_area_facing_east_m2,
            su.roof_aspect_area_facing_south_east_m2,
            su.roof_aspect_area_facing_south_m2,
            su.roof_aspect_area_facing_south_west_m2,
            su.roof_aspect_area_facing_west_m2,
            su.roof_aspect_area_facing_north_west_m2,
            su.roof_aspect_area_indeterminable_m2
        FROM (
            SELECT
                *
            FROM
                iris.epc_assessment
            WHERE uprn = :uprn
            ORDER BY
                match_score desc nulls first,
                lodgement_date desc nulls last,
                id desc
            LIMIT 1) ea
        JOIN iris.structure_unit su ON su.epc_assessment_id = ea.id
        LIMIT 1;
    """


def get_ngd_roof_material_for_building(uprn: str) -> str:
    return f"""
        PREFIX building:  <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data:      <http://ndtp.co.uk/data#>
        PREFIX ies:       <http://informationexchangestandard.org/ont/ies#>

        SELECT ?roofMaterial
        WHERE {{
            data:StructureUnit_{uprn} ies:isPartOf ?building .
            ?roof ies:isPartOf ?building .
            ?roofState a building:RoofState ;
                      ies:isStateOf ?roof ;
                      building:isMadeOf ?roofMaterial .
        }}
        LIMIT 1
    """


def get_ngd_solar_panel_presence_for_building(uprn: str) -> str:
    return f"""
        PREFIX building:  <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data:      <http://ndtp.co.uk/data#>
        PREFIX ies:       <http://informationexchangestandard.org/ont/ies#>

        SELECT ?solarPanelPresence
        WHERE {{
            data:StructureUnit_{uprn} ies:isPartOf ?building .
            ?state ies:isStateOf ?building ;
                   a ?solarPanelPresence .
            VALUES ?solarPanelPresence {{
                building:NoSolarPanels
                building:HasSolarPanels
                building:UnknownSolarPanelPresence
            }}
        }}
        LIMIT 1
    """


def get_ngd_roof_shape_for_building(uprn: str) -> str:
    return f"""
        PREFIX building:  <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data:      <http://ndtp.co.uk/data#>
        PREFIX ies:       <http://informationexchangestandard.org/ont/ies#>

        SELECT DISTINCT ?roofShape
        WHERE {{
            data:StructureUnit_{uprn} ies:isPartOf ?building .
            ?shapeState ies:isStateOf ?building ;
                        a building:RoofState ;
                        a ?roofShape .
            VALUES ?roofShape {{
                building:PitchedRoofShape
                building:FlatRoofShape
                building:MixedRoofShape
                building:UnknownRoofShape
            }}
        }}
        LIMIT 1
    """


def get_ngd_roof_aspect_areas_for_building(uprn: str) -> str:
    return f"""
        PREFIX building:     <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data:         <http://ndtp.co.uk/data#>
        PREFIX ies:          <http://informationexchangestandard.org/ont/ies#>
        PREFIX qudt:         <http://qudt.org/schema/qudt/>
        PREFIX unit:         <http://qudt.org/vocab/unit/>
        PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>

        SELECT ?direction ?m2
        WHERE {{
            data:StructureUnit_{uprn} ies:isPartOf ?building .
            ?roof ies:isPartOf ?building .
            ?roofState a building:RoofState ; ies:isStateOf ?roof .

            ?aspect a ?directionClass ;
                    ies:isPartOf ?roofState ;
                    building:hasCombinedSurfaceArea [
                        building:hasQuantity [
                            qudt:hasQuantityKind quantitykind:Area ;
                            qudt:unit unit:M2 ;
                            qudt:value ?m2
                        ]
                    ] .

            VALUES ?directionClass {{
                building:NorthFacingRoofSectionSum
                building:NorthEastFacingRoofSectionSum
                building:EastFacingRoofSectionSum
                building:SouthEastFacingRoofSectionSum
                building:SouthFacingRoofSectionSum
                building:SouthWestFacingRoofSectionSum
                building:WestFacingRoofSectionSum
                building:NorthWestFacingRoofSectionSum
                building:AreaIndeterminableRoofSectionSum
            }}
            BIND(STRAFTER(STR(?directionClass), "#") AS ?direction)
        }}
    """


def get_buildings_in_bounding_box_query() -> str:
    return """
        WITH filtered_buildings AS (
            SELECT uprn, first_line_of_address, toid, point
            FROM iris.building
            WHERE is_residential = true AND
                point && ST_MakeEnvelope(:min_long, :min_lat, :max_long, :max_lat, :srid)
                AND ST_Intersects(point, ST_MakeEnvelope(:min_long, :min_lat, :max_long, :max_lat, :srid))
        )
        SELECT
            fb.uprn,
            fb.first_line_of_address,
            fb.toid,
            fb.point,
            ea.epc_rating,
            su.type as structure_unit_type
        FROM
            filtered_buildings fb
        LEFT JOIN LATERAL (
            SELECT
                id,
                uprn,
                epc_rating,
                lodgement_date
            FROM
                iris.epc_assessment
            WHERE
                uprn = fb.uprn
            ORDER BY
                match_score desc nulls first,
                lodgement_date desc nulls last,
                id desc
            LIMIT 1
        ) ea ON
            TRUE
        LEFT JOIN iris.structure_unit su
        ON
            su.epc_assessment_id = ea.id;
    """


def get_filterable_buildings_in_bounding_box_query() -> str:
    return """
        WITH filtered_buildings AS (
            SELECT uprn, toid, post_code, point
            FROM iris.building
            WHERE is_residential = true
                AND point && ST_MakeEnvelope(:min_long, :min_lat, :max_long, :max_lat, :srid)
                AND ST_Intersects(point, ST_MakeEnvelope(:min_long, :min_lat, :max_long, :max_lat, :srid))
        )
        SELECT
            fb.uprn, fb.toid, fb.post_code,
            su.built_form, su.fuel_type,
            ea.lodgement_date, su.window_glazing,
            su.wall_construction, su.wall_insulation,
            su.floor_construction, su.floor_insulation,
            su.has_roof_solar_panels, su.roof_material,
            su.roof_aspect_area_facing_north_m2,
            su.roof_aspect_area_facing_north_east_m2,
            su.roof_aspect_area_facing_north_west_m2,
            su.roof_aspect_area_facing_east_m2,
            su.roof_aspect_area_facing_south_m2,
            su.roof_aspect_area_facing_south_east_m2,
            su.roof_aspect_area_facing_south_west_m2,
            su.roof_aspect_area_facing_west_m2,
            su.roof_construction, su.roof_insulation,
            su.roof_insulation_thickness
        FROM
            filtered_buildings fb
        LEFT JOIN LATERAL (
            SELECT
                id,
                uprn,
                epc_rating,
                lodgement_date
            FROM
                iris.epc_assessment
            WHERE
                uprn = fb.uprn
            ORDER BY
                match_score desc nulls first,
                lodgement_date desc nulls last,
                id desc
            LIMIT 1
        ) ea ON
            TRUE
        LEFT JOIN iris.structure_unit su
        ON
            su.epc_assessment_id = ea.id;
    """


def get_statistics_for_wards() -> str:
    return """
        PREFIX stats: <http://ndtp.co.uk/stats#>

        SELECT ?wardName ?EPC_Rating_A ?EPC_Rating_B ?EPC_Rating_C ?EPC_Rating_D ?EPC_Rating_E ?EPC_Rating_F ?EPC_Rating_G ?No_EPC_Rating
        WHERE {
            GRAPH <http://ndtp.co.uk/epc-ward-statistics> {
                ?stats a stats:EPCWardStats ;
                            stats:wardName ?wardName ;
                            stats:EPC_Rating_A ?EPC_Rating_A ;
                            stats:EPC_Rating_B ?EPC_Rating_B ;
                            stats:EPC_Rating_C ?EPC_Rating_C ;
                            stats:EPC_Rating_D ?EPC_Rating_D ;
                            stats:EPC_Rating_E ?EPC_Rating_E ;
                            stats:EPC_Rating_F ?EPC_Rating_F ;
                            stats:EPC_Rating_G ?EPC_Rating_G ;
                            stats:No_EPC_Rating ?No_EPC_Rating .
            }
        }
        ORDER BY ?wardName
    """


def get_flagged_buildings() -> str:
    return """
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX ies: <http://informationexchangestandard.org/ont/ies#>
        SELECT ?toid ?uprn ?flag WHERE {
            ?flag a ?flagType;
                ies:interestedIn ?structureUnitState .
            ?structureUnitState a building:StructureUnitState ;
                ies:isStateOf ?structureUnit .
            ?structureUnit a building:StructureUnit ;
                ies:isIdentifiedBy ?uprn ;
                ies:isIdentifiedBy ?_toid .

            ?uprn a building:UPRN .
            ?_toid a ies:TOID ;
                ies:representationValue ?toid .

            FILTER NOT EXISTS { ?flag_assessment ies:assessed ?flag . }
        }
        """


def get_flag_history(uprn: str) -> str:
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ies: <http://informationexchangestandard.org/ont/ies#>
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data: <http://ndtp.co.uk/data#>

        SELECT ?uprn ?flag ?flagType ?retrofitterName ?flagDate ?assessmentDate ?assessorName ?assessmentReason
        WHERE {{
            ?uprn a building:UPRN .
            ?uprn ies:representationValue '{uprn}' .

            ?structureUnit ies:isIdentifiedBy ?uprn;
                a building:StructureUnit .
            ?structureUnitState a building:StructureUnitState ;
                ies:isStateOf ?structureUnit .

            ?flag a ?flagType;
                ies:interestedIn ?structureUnitState ;
                ies:inPeriod ?flagDate ;
                ies:isStateOf ?retrofitter .
            ?retrofitter ies:hasName ?_retrofitterName .
            ?_retrofitterName ies:representationValue ?retrofitterName .

                OPTIONAL {{
                    ?assessment a ?assessmentReason ;
                        ies:assessed ?flag ;
                        ies:inPeriod ?assessmentDate ;
                        ies:assessor ?assessor .
                    ?assessor ies:hasName ?_assessorName .
                    ?_assessorName ies:representationValue ?assessorName .
                }}
        }}
    """


def area_level_to_column(area_level: str) -> str:
    try:
        return {
            "region": "region_name",
            "county": "county_name",
            "district": "district_name",
            "ward": "ward_name",
        }[area_level]
    except KeyError:
        raise ValueError(
            f"Invalid area_level '{area_level}'. Must be one of region, county, district, ward."
        )


def _wales_grouped_column(column: str) -> str:
    """Returns a CASE expression that groups Welsh regions into 'Wales'."""
    return f"""CASE
                WHEN {column} IN ({WELSH_REGIONS_SQL})
                THEN 'Wales'
                ELSE {column}
            END"""


def _get_epc_rating_query_with_polygon(per_region: bool, polygon: str):
    """Build EPC rating query for polygon filter using building_epc_analytics."""
    params = {"polygon": polygon}
    where_conditions = [
        EPC_ACTIVE_TRUE,
        "ST_Within(point, ST_GeomFromGeoJSON(:polygon))",
    ]
    if per_region:
        where_conditions.append("region_name IS NOT NULL AND region_name != ''")

    region_select = (
        _wales_grouped_column("region_name") + " AS region_name," if per_region else ""
    )
    group_by = "GROUP BY " + _wales_grouped_column("region_name") if per_region else ""

    query = f"""
        SELECT {region_select}
                COUNT(*) FILTER (WHERE epc_rating = 'A') AS epc_a,
                COUNT(*) FILTER (WHERE epc_rating = 'B') AS epc_b,
                COUNT(*) FILTER (WHERE epc_rating = 'C') AS epc_c,
                COUNT(*) FILTER (WHERE epc_rating = 'D') AS epc_d,
                COUNT(*) FILTER (WHERE epc_rating = 'E') AS epc_e,
                COUNT(*) FILTER (WHERE epc_rating = 'F') AS epc_f,
                COUNT(*) FILTER (WHERE epc_rating = 'G') AS epc_g
        FROM iris.building_epc_analytics
        WHERE {" AND ".join(where_conditions)}
        {group_by};
    """
    return query, params


def _get_epc_rating_query_from_aggregates(
    per_region: bool, area_level: str, area_names: list
):
    """Build EPC rating query from pre-aggregated data."""
    params = {}
    where_conditions = [
        "snapshot_date = (SELECT MAX(snapshot_date) FROM iris.building_epc_analytics_aggregates)"
    ]

    if area_level and area_names:
        area_names = expand_wales_region(area_names)
        where_conditions.append(
            f"{area_level_to_column(area_level)} = ANY(:area_names)"
        )
        params["area_names"] = area_names

    if per_region:
        where_conditions.append("region_name IS NOT NULL AND region_name != ''")

    region_select = (
        _wales_grouped_column("region_name") + " AS region_name," if per_region else ""
    )
    group_by = "GROUP BY " + _wales_grouped_column("region_name") if per_region else ""

    query = f"""
        SELECT {region_select}
                SUM(count_rating_a) AS epc_a,
                SUM(count_rating_b) AS epc_b,
                SUM(count_rating_c) AS epc_c,
                SUM(count_rating_d) AS epc_d,
                SUM(count_rating_e) AS epc_e,
                SUM(count_rating_f) AS epc_f,
                SUM(count_rating_g) AS epc_g
        FROM iris.building_epc_analytics_aggregates
        WHERE {" AND ".join(where_conditions)}
        {group_by};
    """
    return query, params


def get_count_of_epc_rating_query(
    per_region: bool = False,
    polygon: str = None,
    area_level: str = None,
    area_names: list = None,
):
    if polygon:
        return _get_epc_rating_query_with_polygon(per_region, polygon)
    return _get_epc_rating_query_from_aggregates(per_region, area_level, area_names)


def get_percentage_of_buildings_attributes_per_region_query(
    polygon: str = None, area_level: str = None, area_names: list = None
):
    where_conditions = []
    params = {}

    def percentage_column(filter, alias):
        return f"""
        ROUND(
            100.0 * AVG(CASE WHEN {filter} THEN 1 ELSE 0 END)::numeric,
            2
        ) AS {alias}
    """

    where_conditions.append(EPC_ACTIVE_TRUE)

    if polygon:
        where_conditions.append("ST_Within(point, ST_GeomFromGeoJSON(:polygon))")
        params["polygon"] = polygon
    elif area_level and area_names:
        area_names = expand_wales_region(area_names)
        where_conditions.append(
            f"{area_level_to_column(area_level)} = ANY(:area_names)"
        )
        params["area_names"] = area_names

    where_clause = "WHERE " + " AND ".join(where_conditions)

    query = f"""
        SELECT {_wales_grouped_column("region_name")} AS region_name,
                {percentage_column("window_glazing = 'SingleGlazing'", "percentage_single_glazing")},
                {percentage_column("window_glazing IN ('DoubleGlazing', 'DoubleGlazingBefore2002', 'DoubleGlazingAfter2002')", "percentage_double_glazing")},
                {percentage_column("window_glazing = 'TripleGlazing'", "percentage_triple_glazing")},
                {percentage_column("roof_insulation_thickness = '0mm'", "percentage_no_insulation")},
                {percentage_column("roof_insulation_thickness IN ('12mm', '25mm', '50mm', '75mm', '100mm')", "percentage_insulation_1_100mm")},
                {percentage_column("roof_insulation_thickness IN ('125mm', '150mm', '150+mm', '175mm', '200mm')", "percentage_insulation_101_200mm")},
                {percentage_column("roof_insulation_thickness IN ('225mm', '250mm', '270mm', '300mm')", "percentage_insulation_201_300mm")},
                {percentage_column("roof_insulation_thickness IN ('350mm', '400mm', '400+mm')", "percentage_insulation_over_300mm")},
                {percentage_column("floor_construction = 'Suspended'", "percentage_suspended_flooring")},
                {percentage_column("roof_construction = 'PitchedRoof'", "percentage_pitched_roof")},
                {percentage_column("wall_construction = 'CavityWall'", "percentage_cavity_wall")},
                {percentage_column("has_roof_solar_panels", "percentage_roof_solar_panels")}
        FROM iris.building_epc_analytics
        {where_clause}
        GROUP BY {_wales_grouped_column("region_name")};
    """

    return query, params


def get_fuel_types_by_building_type_query(
    polygon: str = None, area_level: str = None, area_names: list = None
):
    where_conditions = []
    params = {}

    where_conditions.append(EPC_ACTIVE_TRUE)

    if polygon:
        where_conditions.append("ST_Within(point, ST_GeomFromGeoJSON(:polygon))")
        params["polygon"] = polygon
    elif area_level and area_names:
        area_names = expand_wales_region(area_names)
        where_conditions.append(
            f"{area_level_to_column(area_level)} = ANY(:area_names)"
        )
        params["area_names"] = area_names

    where_conditions.append("type IS NOT NULL")
    where_conditions.append("fuel_type IS NOT NULL")

    where_clause = "WHERE " + " AND ".join(where_conditions)

    query = f"""
        SELECT type AS building_type,
               fuel_type,
               COUNT(*) as count
        FROM iris.building_epc_analytics
        {where_clause}
        GROUP BY type, fuel_type
        ORDER BY type, count DESC;
    """

    return query, params


def get_national_avg_sap_rating_overtime_query():
    """Get national average SAP rating over time using pre-calculated aggregates."""
    query = """
        SELECT
            snapshot_date as date,
            SUM(sum_sap_rating) / NULLIF(SUM(active_epc_count), 0) as avg_sap_rating
        FROM iris.building_epc_analytics_aggregates
        GROUP BY snapshot_date
        ORDER BY snapshot_date ASC;
    """
    return query


def get_filtered_avg_sap_rating_overtime_query(
    polygon: str = None, area_level: str = None, area_names: list = None
):
    """Get filtered average SAP rating over time for a specific polygon area or named areas."""

    if not polygon and not (area_level and area_names):
        raise ValueError(
            "either polygon or area_level/area_names filter must be provided"
        )

    if polygon:
        query = """
            SELECT
                unnest(active_snapshots) as date,
                AVG(sap_rating) as avg_sap_rating
            FROM iris.building_epc_analytics
            WHERE active_snapshots IS NOT NULL
              AND ST_Within(point, ST_GeomFromGeoJSON(:polygon))
            GROUP BY date
            ORDER BY date ASC;
        """
        return query, {"polygon": polygon}

    area_names = expand_wales_region(area_names)
    query = f"""
        SELECT
            snapshot_date as date,
            SUM(sum_sap_rating) / NULLIF(SUM(active_epc_count), 0) as avg_sap_rating
        FROM iris.building_epc_analytics_aggregates
        WHERE {area_level_to_column(area_level)} = ANY(:area_names)
        GROUP BY snapshot_date
        ORDER BY snapshot_date ASC;
    """
    return query, {"area_names": area_names}


def get_buildings_affected_by_extreme_weather_data_query(
    polygon: str = None, area_level: str = None, area_names: list = None
):
    """Get buildings affected by extreme weather, optionally filtered by area."""
    params = {}

    if polygon:
        params["polygon"] = polygon
        filter_condition = "ST_Within(point, ST_GeomFromGeoJSON(:polygon))"
    elif area_level and area_names:
        area_names = expand_wales_region(area_names)
        params["area_names"] = area_names
        filter_condition = f"{area_level_to_column(area_level)} = ANY(:area_names)"
    else:
        filter_condition = "FALSE"

    query = f"""
        SELECT
            COUNT(*) AS number_of_buildings,
            COUNT(*) FILTER (WHERE {filter_condition}) AS filtered_number_of_buildings,
            affected_by_icing_days,
            affected_by_hsds,
            affected_by_wdr
        FROM iris.building_extreme_weather_analytics
        GROUP BY affected_by_icing_days, affected_by_hsds, affected_by_wdr
    """

    return query, params


def get_number_of_in_date_and_expired_epcs_query(
    polygon: str = None, area_level: str = None, area_names: list = None
):
    """Get in-date and expired EPC counts over time, optionally filtered by area."""
    params = {}

    # For polygon filters, calculate dynamically from building_epc_analytics (spatial query required)
    if polygon:
        params["polygon"] = polygon

        query = """
            WITH snapshot_dates AS (
                SELECT generate_series(
                    DATE_TRUNC('year', (SELECT MIN(lodgement_date) FROM iris.building_epc_analytics WHERE lodgement_date IS NOT NULL))::date + interval '1 year' - interval '1 day',
                    DATE_TRUNC('year', CURRENT_DATE)::date + interval '1 year' - interval '1 day',
                    interval '1 year'
                )::date as snapshot_date
            ),
            filtered_buildings AS (
                SELECT uprn, lodgement_date, active_snapshots
                FROM iris.building_epc_analytics
                WHERE active_snapshots IS NOT NULL
                  AND ST_Within(point, ST_GeomFromGeoJSON(:polygon))
            ),
            issued_counts AS (
                SELECT
                    sd.snapshot_date,
                    COUNT(DISTINCT fb.uprn) as total_issued_count
                FROM snapshot_dates sd
                CROSS JOIN filtered_buildings fb
                WHERE fb.lodgement_date <= sd.snapshot_date
                GROUP BY sd.snapshot_date
            ),
            active_counts AS (
                SELECT
                    unnest(active_snapshots) as snapshot_date,
                    COUNT(*) as active_epc_count
                FROM filtered_buildings
                GROUP BY unnest(active_snapshots)
            )
            SELECT
                ic.snapshot_date AS year,
                COALESCE(ac.active_epc_count, 0) AS active,
                (ic.total_issued_count - COALESCE(ac.active_epc_count, 0)) AS expired
            FROM issued_counts ic
            LEFT JOIN active_counts ac ON ic.snapshot_date = ac.snapshot_date
            ORDER BY ic.snapshot_date;
        """
        return query, params

    where_conditions = []
    if area_level and area_names:
        area_names = expand_wales_region(area_names)
        where_conditions.append(
            f"{area_level_to_column(area_level)} = ANY(:area_names)"
        )
        params["area_names"] = area_names

    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    query = f"""
        SELECT
            snapshot_date AS year,
            SUM(active_epc_count) AS active,
            SUM(expired_epc_count) AS expired
        FROM iris.building_epc_analytics_aggregates
        {where_clause}
        GROUP BY snapshot_date
        ORDER BY snapshot_date;
    """

    return query, params


def get_region_names_query() -> str:
    return f"""
        SELECT DISTINCT {_wales_grouped_column("region_name")} AS region_name
        FROM iris.building_epc_analytics
        WHERE region_name IS NOT NULL
        ORDER BY region_name
    """


def get_county_names_query() -> str:
    return """
        SELECT DISTINCT county_name
        FROM iris.building_epc_analytics
        WHERE county_name IS NOT NULL
        ORDER BY county_name
    """


def get_district_names_query() -> str:
    return """
        SELECT DISTINCT district_name
        FROM iris.building_epc_analytics
        WHERE district_name IS NOT NULL
        ORDER BY district_name
    """


def get_ward_names_query() -> str:
    return """
        SELECT DISTINCT ward_name
        FROM iris.building_epc_analytics
        WHERE ward_name IS NOT NULL
        ORDER BY ward_name
    """


def get_count_of_epc_rating_by_area_level_query(
    group_by_level: str,
    filter_area_level: str = None,
    filter_area_names: list = None,
):
    params = {}
    where_conditions = []

    group_column = area_level_to_column(group_by_level)

    if filter_area_level and filter_area_names:
        filter_area_names = expand_wales_region(filter_area_names)
        filter_column = area_level_to_column(filter_area_level)
        where_conditions.append(f"{filter_column} = ANY(:filter_area_names)")
        params["filter_area_names"] = filter_area_names

    where_conditions.append(f"{group_column} IS NOT NULL AND {group_column} != ''")

    where_conditions.append(
        "snapshot_date = (SELECT MAX(snapshot_date) FROM iris.building_epc_analytics_aggregates)"
    )

    where_clause = "WHERE " + " AND ".join(where_conditions)

    if group_by_level == "region":
        area_select = _wales_grouped_column(group_column) + " AS area_name"
        group_by = "GROUP BY " + _wales_grouped_column(group_column)
    else:
        area_select = f"{group_column} AS area_name"
        group_by = f"GROUP BY {group_column}"

    query = f"""
        SELECT
            {area_select},
            SUM(count_rating_a) AS epc_a,
            SUM(count_rating_b) AS epc_b,
            SUM(count_rating_c) AS epc_c,
            SUM(count_rating_d) AS epc_d,
            SUM(count_rating_e) AS epc_e,
            SUM(count_rating_f) AS epc_f,
            SUM(count_rating_g) AS epc_g
        FROM iris.building_epc_analytics_aggregates
        {where_clause}
        {group_by};
    """

    return query, params


def _get_feature_query_config(feature: str) -> dict:
    """Returns select clause and where condition for a given feature."""
    configs = {
        "glazing_types": {
            "select": """CASE
                WHEN window_glazing IN ('DoubleGlazing', 'DoubleGlazingAfter2002', 'DoubleGlazingBefore2002')
                THEN 'DoubleGlazing'
                ELSE window_glazing
            END""",
            "where": "window_glazing IS NOT NULL AND window_glazing != ''",
        },
        "fuel_types": {
            "select": "fuel_type",
            "where": "fuel_type IS NOT NULL AND fuel_type != ''",
        },
        "wall_construction": {
            "select": "wall_construction",
            "where": "wall_construction IS NOT NULL AND wall_construction != ''",
        },
        "wall_insulation": {
            "select": "wall_insulation",
            "where": "wall_insulation IS NOT NULL AND wall_insulation != ''",
        },
        "floor_construction": {
            "select": "floor_construction",
            "where": "floor_construction IS NOT NULL AND floor_construction != ''",
        },
        "floor_insulation": {
            "select": "floor_insulation",
            "where": "floor_insulation IS NOT NULL AND floor_insulation != ''",
        },
        "roof_construction": {
            "select": "roof_construction",
            "where": "roof_construction IS NOT NULL AND roof_construction != ''",
        },
        "roof_material": {
            "select": "roof_material",
            "where": "roof_material IS NOT NULL AND roof_material != ''",
        },
        "roof_insulation": {
            "select": "roof_insulation",
            "where": "roof_insulation IS NOT NULL AND roof_insulation != ''",
        },
        "roof_insulation_thickness": {
            "select": "roof_insulation_thickness",
            "where": "roof_insulation_thickness IS NOT NULL AND roof_insulation_thickness != ''",
        },
        "solar_panels": {
            "select": "CASE WHEN has_roof_solar_panels THEN 'Yes' ELSE 'No' END",
            "where": "has_roof_solar_panels IS NOT NULL",
        },
        "roof_aspect": {
            "select": "direction",
            "where": "direction IS NOT NULL",
            "from_clause": """iris.building_epc_analytics
            CROSS JOIN LATERAL (
                VALUES
                    (CASE WHEN roof_aspect_area_facing_north_m2 > 0 THEN 'North' END),
                    (CASE WHEN roof_aspect_area_facing_north_east_m2 > 0 THEN 'NorthEast' END),
                    (CASE WHEN roof_aspect_area_facing_east_m2 > 0 THEN 'East' END),
                    (CASE WHEN roof_aspect_area_facing_south_east_m2 > 0 THEN 'SouthEast' END),
                    (CASE WHEN roof_aspect_area_facing_south_m2 > 0 THEN 'South' END),
                    (CASE WHEN roof_aspect_area_facing_south_west_m2 > 0 THEN 'SouthWest' END),
                    (CASE WHEN roof_aspect_area_facing_west_m2 > 0 THEN 'West' END),
                    (CASE WHEN roof_aspect_area_facing_north_west_m2 > 0 THEN 'NorthWest' END)
            ) AS directions(direction)""",
        },
    }
    if feature not in configs:
        raise ValueError(f"Invalid feature: {feature}")
    return configs[feature]


def get_count_of_epc_rating_by_features_query(
    feature: str, polygon: str = None, area_level: str = None, area_names: list = None
):
    config = _get_feature_query_config(feature)
    params = {}
    where_conditions = [EPC_ACTIVE_TRUE, "epc_rating IS NOT NULL", config["where"]]

    if polygon:
        where_conditions.append("ST_Within(point, ST_GeomFromGeoJSON(:polygon))")
        params["polygon"] = polygon
    elif area_level and area_names:
        area_names = expand_wales_region(area_names)
        filter_column = area_level_to_column(area_level)
        where_conditions.append(f"{filter_column} = ANY(:area_names)")
        params["area_names"] = area_names

    where_clause = "WHERE " + " AND ".join(where_conditions)
    from_clause = config.get("from_clause", "iris.building_epc_analytics")

    query = f"""
        SELECT
            {config["select"]} as name,
            COUNT(*) FILTER (WHERE epc_rating = 'A') as epc_a,
            COUNT(*) FILTER (WHERE epc_rating = 'B') as epc_b,
            COUNT(*) FILTER (WHERE epc_rating = 'C') as epc_c,
            COUNT(*) FILTER (WHERE epc_rating = 'D') as epc_d,
            COUNT(*) FILTER (WHERE epc_rating = 'E') as epc_e,
            COUNT(*) FILTER (WHERE epc_rating = 'F') as epc_f,
            COUNT(*) FILTER (WHERE epc_rating = 'G') as epc_g
        FROM {from_clause}
        {where_clause}
        GROUP BY name;
    """

    return query, params


def get_epc_ratings_overtime_query(
    polygon: str = None, area_level: str = None, area_names: list = None
):
    params = {}

    if polygon:
        query = """
            SELECT
                unnest(active_snapshots) as date,
                COUNT(*) FILTER (WHERE epc_rating = 'A') AS epc_a,
                COUNT(*) FILTER (WHERE epc_rating = 'B') AS epc_b,
                COUNT(*) FILTER (WHERE epc_rating = 'C') AS epc_c,
                COUNT(*) FILTER (WHERE epc_rating = 'D') AS epc_d,
                COUNT(*) FILTER (WHERE epc_rating = 'E') AS epc_e,
                COUNT(*) FILTER (WHERE epc_rating = 'F') AS epc_f,
                COUNT(*) FILTER (WHERE epc_rating = 'G') AS epc_g
            FROM iris.building_epc_analytics
            WHERE active_snapshots IS NOT NULL
              AND ST_Within(point, ST_GeomFromGeoJSON(:polygon))
            GROUP BY date
            ORDER BY date ASC;
        """
        params["polygon"] = polygon
    else:
        where_clause = ""
        if area_level and area_names:
            area_names = expand_wales_region(area_names)
            where_clause = (
                f"WHERE {area_level_to_column(area_level)} = ANY(:area_names)"
            )
            params["area_names"] = area_names

        query = f"""
            SELECT
                snapshot_date as date,
                SUM(count_rating_a) as epc_a,
                SUM(count_rating_b) as epc_b,
                SUM(count_rating_c) as epc_c,
                SUM(count_rating_d) as epc_d,
                SUM(count_rating_e) as epc_e,
                SUM(count_rating_f) as epc_f,
                SUM(count_rating_g) as epc_g
            FROM iris.building_epc_analytics_aggregates
            {where_clause}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC;
        """

    return query, params


def get_sap_rating_overtime_by_property_type_query(polygon: str):
    """Get average SAP rating over time grouped by property type for a polygon area."""
    query = """
        SELECT
            unnest(active_snapshots) as date,
            type as name,
            AVG(sap_rating) as avg_sap_rating
        FROM iris.building_epc_analytics
        WHERE active_snapshots IS NOT NULL
          AND type IS NOT NULL
          AND type != ''
          AND ST_Within(point, ST_GeomFromGeoJSON(:polygon))
        GROUP BY date, type
        ORDER BY date ASC, type ASC;
    """
    return query, {"polygon": polygon}


def get_sap_rating_overtime_by_area_query(
    group_by_level: str,
    filter_area_level: str = None,
    filter_area_names: list = None,
):
    """Get average SAP rating over time for each area at the specified grouping level."""
    params = {}
    where_conditions = []

    group_column = area_level_to_column(group_by_level)

    if filter_area_level and filter_area_names:
        filter_area_names = expand_wales_region(filter_area_names)
        filter_column = area_level_to_column(filter_area_level)
        where_conditions.append(f"{filter_column} = ANY(:filter_area_names)")
        params["filter_area_names"] = filter_area_names

    where_conditions.append(f"{group_column} IS NOT NULL AND {group_column} != ''")

    where_clause = "WHERE " + " AND ".join(where_conditions)

    if group_by_level == "region":
        area_select = _wales_grouped_column(group_column) + " AS name"
        group_by = f"snapshot_date, {_wales_grouped_column(group_column)}"
    else:
        area_select = f"{group_column} AS name"
        group_by = f"snapshot_date, {group_column}"

    query = f"""
        SELECT
            snapshot_date as date,
            {area_select},
            SUM(sum_sap_rating) / NULLIF(SUM(active_epc_count), 0) as avg_sap_rating
        FROM iris.building_epc_analytics_aggregates
        {where_clause}
        GROUP BY {group_by}
        ORDER BY date ASC, name ASC;
    """

    return query, params
