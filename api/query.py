# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

def get_building(uprn: str) -> str:
    return f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ies: <http://informationexchangestandard.org/ont/ies#>
        PREFIX building: <http://ies.data.gov.uk/ontology/ies-building1#>
        PREFIX data: <http://ndtp.co.uk/data#>

        SELECT ?uprn ?lodgementDate ?builtForm ?structureUnitType WHERE {{
            ?uprn a building:UPRN .
            ?uprn ies:representationValue '{uprn}' .
            
            ?structureUnit ies:isIdentifiedBy ?uprn .
            ?structureUnit a building:StructureUnit .
            ?structureUnitState a building:StructureUnitState .
            ?structureUnitState ies:isStateOf ?structureUnit .
            
            ?epc_result building:lodgementDate ?lodgementDate .
            ?epc_result ies:isParticipantIn ?epc_assessment .
            ?epc_assessment building:assessedStateForEnergyPerformance ?structureUnitState .
            
            ?_bf a ?builtForm .
            ?builtForm a building:BuiltForm .
            ?_bf ies:isStateOf ?structureUnit .
            
            ?_sut a ?structureUnitType .
            ?structureUnitType a building:StructureUnitType .
            ?_sut ies:isStateOf ?structureUnit .
        }}
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
            ?uprn a building:UPRN .
            ?uprn ies:representationValue '{uprn}' .
            
            ?structureUnit ies:isIdentifiedBy ?uprn .
            ?structureUnit a building:StructureUnit .
            ?structureUnitState a building:StructureUnitState .
            ?structureUnitState ies:isStateOf ?structureUnit .
            
            ?_rc a ?roofConstruction .
            ?roofConstruction a building:RoofConstruction .
            ?_rc ies:isPartOf ?structureUnitState .
            
            ?_ri a ?roofInsulation .
            ?roofInsulation a building:RoofInsulationLocation .
            ?_ri ies:isPartOf ?structureUnitState .
            
            OPTIONAL {{
                ?_rit a ?roofInsulationThickness .
                ?roofInsulationThickness a building:RoofInsulationThickness .
                ?_rit ies:isPartOf ?structureUnitState .
            }}        
        }}
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
        ?uprn a building:UPRN .
        ?uprn ies:representationValue '{uprn}' .
        
        ?structureUnit ies:isIdentifiedBy ?uprn .
        ?structureUnit a building:StructureUnit .
        ?structureUnitState a building:StructureUnitState .
        ?structureUnitState ies:isStateOf ?structureUnit .
        
        ?_fc a ?floorConstruction .
        ?floorConstruction a building:FloorConstruction .
        ?_fc ies:isPartOf ?structureUnitState .
        
        ?_fi a ?floorInsulation .
        ?floorInsulation a building:FloorInsulation .
        ?_fi ies:isPartOf ?structureUnitState .
        
        }}
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
            ?uprn a building:UPRN .
            ?uprn ies:representationValue '{uprn}' .
            
            ?structureUnit ies:isIdentifiedBy ?uprn .
            ?structureUnit a building:StructureUnit .
            ?structureUnitState a building:StructureUnitState .
            ?structureUnitState ies:isStateOf ?structureUnit .
            
            ?_wc a ?wallConstruction .
            ?wallConstruction a building:WallConstruction .
            ?_wc ies:isPartOf ?structureUnitState .
            
            ?_wi a ?wallInsulation .
            ?wallInsulation a building:WallInsulation .
            ?_wi ies:isPartOf ?structureUnitState .
            
            ?_wg a ?windowGlazing .
            ?windowGlazing a building:GlazingType .
            ?_wg ies:isPartOf ?structureUnitState .
            
        }}
        LIMIT 1
    """
    
def get_buildings_in_bounding_box_query(polygon: str) -> str:
    return f"""
    PREFIX data: <http://ndtp.co.uk/data#>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

    SELECT ?uprn ?firstLineOfAddress ?toid ?point ?epcRating ?structureUnitType
    WHERE {{
        GRAPH <http://ndtp.co.uk/building-geo-mapping> {{ 
            ?uprn geo:asWKT ?point .
            ?uprn data:hasFirstLineOfAddress ?firstLineOfAddress .
            ?uprn data:hasToid ?toid .
            ?uprn data:hasEPCRating ?epcRating .
            ?uprn data:hasStructureUnitType ?structureUnitType .
            
            FILTER(geof:sfIntersects(?point, "{polygon}"^^geo:wktLiteral))
        }}
    }}
    """

def get_detailed_buildings_in_bounding_box_query(polygon: str) -> str:
    return f"""
        PREFIX data: <http://ndtp.co.uk/data#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

        SELECT ?uprn ?point ?postcode ?windowGlazing ?wallConstruction ?wallInsulation ?floorConstruction ?floorInsulation ?roofConstruction ?roofInsulation ?roofInsulationThickness
        WHERE {{ 
            GRAPH <http://ndtp.co.uk/detailed-building-geo-mapping> {{
                ?uprn geo:asWKT ?point ;
                    data:hasPostcode ?postcode ;
                    data:hasWindowGlazing ?windowGlazing ;
                    data:hasWallConstruction ?wallConstruction ;
                    data:hasWallInsulation ?wallInsulation ;
                    data:hasFloorConstruction ?floorConstruction ;
                    data:hasFloorInsulation ?floorInsulation .
                OPTIONAL {{
                    ?uprn data:hasRoofConstruction ?roofConstruction ;
                        data:hasRoofInsulation ?roofInsulation ;
                        data:hasRoofInsulationThickness ?roofInsulationThickness .
                }}
                FILTER(geof:sfIntersects(?point, "{polygon}"^^geo:wktLiteral))
            }}
        }}
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