# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


EPC_ACTIVE_TRUE = "epc_active = true"


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
                ?_bf a ?builtForm .
                ?builtForm a building:BuiltForm .
                ?_bf ies:isStateOf ?structureUnit .
            }}

            OPTIONAL {{
                ?_sut a ?structureUnitType .
                ?structureUnitType a building:StructureUnitType .
                ?_sut ies:isStateOf ?structureUnit .
            }}
        }} ORDER BY DESC(?lodgementDate)
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
        }} ORDER BY DESC(?lodgementDate)
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
            ?_fc a ?floorConstruction .
            ?floorConstruction a building:FloorConstruction .
            ?_fc ies:isPartOf ?structureUnitState .
        }}

        OPTIONAL {{
            ?_fi a ?floorInsulation .
            ?floorInsulation a building:FloorInsulation .
            ?_fi ies:isPartOf ?structureUnitState .
        }}

        }} ORDER BY DESC(?lodgementDate)
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

        }} ORDER BY DESC(?lodgementDate)
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
                    }} ORDER BY DESC(?lodgement) LIMIT 1
            }}
                GRAPH <http://ndtp.com/graph/heating-v2> {{
                        ?structureUnitState building:isServicedBy ?heatingSystem .
                        ?heatingSystem building:isOperableWithFuel ?fuelType .
            }}
        }}
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
            ORDER BY
                lodgement_date desc nulls last,
                id desc
            LIMIT 1) ea
        JOIN iris.structure_unit su ON su.epc_assessment_id = ea.id
        WHERE ea.uprn = :uprn
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
            WHERE point && ST_MakeEnvelope(:min_long, :min_lat, :max_long, :max_lat, :srid)
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
            WHERE point && ST_MakeEnvelope(:min_long, :min_lat, :max_long, :max_lat, :srid)
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


def get_count_of_epc_rating_query(per_region: bool = False, polygon: str = None):
    where_conditions = []
    params = {}

    where_conditions.append(EPC_ACTIVE_TRUE)

    if polygon:
        where_conditions.append("ST_Within(point, ST_GeomFromGeoJSON(:polygon))")
        params["polygon"] = polygon

    if per_region:
        where_conditions.append("region_name IS NOT NULL AND region_name != ''")

    where_clause = "WHERE " + " AND ".join(where_conditions)

    query = f"""
        SELECT {"region_name," if per_region else ""}
                COUNT(*) FILTER (WHERE epc_rating = 'A') AS epc_a,
                COUNT(*) FILTER (WHERE epc_rating = 'B') AS epc_b,
                COUNT(*) FILTER (WHERE epc_rating = 'C') AS epc_c,
                COUNT(*) FILTER (WHERE epc_rating = 'D') AS epc_d,
                COUNT(*) FILTER (WHERE epc_rating = 'E') AS epc_e,
                COUNT(*) FILTER (WHERE epc_rating = 'F') AS epc_f,
                COUNT(*) FILTER (WHERE epc_rating = 'G') AS epc_g
        FROM iris.building_epc_analytics
        {where_clause}
        {"GROUP BY region_name" if per_region else ""};
    """

    return query, params


def get_percentage_of_buildings_attributes_per_region_query(polygon: str = None):
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

    where_clause = "WHERE " + " AND ".join(where_conditions)

    query = f"""
        SELECT region_name,
                {percentage_column("has_roof_solar_panels", "percentage_roof_solar_panels")},
                {percentage_column("window_glazing = 'DoubleGlazing'", "percentage_double_glazing")},
                {percentage_column("window_glazing = 'SingleGlazing'", "percentage_single_glazing")},
                {percentage_column("floor_construction = 'SolidFloor'", "percentage_solid_floor")},
                {percentage_column("roof_insulation_thickness = '150mm'", "percentage_roof_insulation_thickness_150mm")},
                {percentage_column("roof_insulation_thickness = '200mm'", "percentage_roof_insulation_thickness_200mm")},
                {percentage_column("roof_insulation_thickness = '250mm'", "percentage_roof_insulation_thickness_250mm")},
                {percentage_column("roof_construction = 'PitchedRoof'", "percentage_pitched_roof")},
                {percentage_column("wall_construction = 'CavityWall'", "percentage_cavity_wall")}
        FROM iris.building_epc_analytics
        {where_clause}
        GROUP BY region_name;
    """

    return query, params


def get_fuel_types_by_building_type_query(polygon: str = None):
    where_conditions = []
    params = {}

    where_conditions.append(EPC_ACTIVE_TRUE)

    if polygon:
        where_conditions.append("ST_Within(point, ST_GeomFromGeoJSON(:polygon))")
        params["polygon"] = polygon

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


def get_avg_sap_rating_overtime_query(polygon: str):
    params = {"polygon": polygon}

    query = """
        WITH all_certs AS (
            -- Get all certificates with their validity period
            SELECT
                uprn,
                lodgement_date,
                sap_rating,
                expiry_date
            FROM iris.building_epc_analytics
            WHERE lodgement_date IS NOT NULL
              AND expiry_date IS NOT NULL
              AND ST_Within(point, ST_GeomFromGeoJSON(:polygon))
        ),
        months_to_check AS (
            -- Get all months where there was certificate activity
            SELECT DISTINCT DATE_TRUNC('month', lodgement_date)::date as month
            FROM all_certs
        ),
        snapshot_per_month AS (
            -- For each month and UPRN, get the latest certificate active at that time
            SELECT
                m.month,
                c.uprn,
                c.sap_rating,
                ROW_NUMBER() OVER (
                    PARTITION BY m.month, c.uprn
                    ORDER BY c.lodgement_date DESC
                ) as rn
            FROM months_to_check m
            JOIN all_certs c
                ON c.lodgement_date <= m.month
                AND c.expiry_date >= m.month
        )
        -- Average the latest active certificate per UPRN for each month
        SELECT
            month as lodgement_date,
            AVG(sap_rating) as avg_sap_rating
        FROM snapshot_per_month
        WHERE rn = 1
        GROUP BY month
        ORDER BY month ASC;
    """

    return query, params
