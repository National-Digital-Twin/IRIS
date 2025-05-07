from api.query import get_building, get_roof_for_building, get_floor_for_building, get_walls_and_windows_for_building, get_buildings_in_bounding_box_query

def building_query_response(uprn):
    return {
        "results": {
            "bindings": [
                { 
                    "uprn": { "type": "uri" , "value": f"http://ndtp.co.uk/data#UPRN_{uprn}" } ,
                    "lodgementDate": { "type": "uri" , "value": "http://iso8601.iso.org/2024-03-30" } ,
                    "builtForm": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#SemiDetached" } ,
                    "structureUnitType": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#House" }
                }
            ]
        }
    }

def roof_query_response(uprn):
    return {
        "results": {
            "bindings": [
            {
                "uprn": { "type": "uri" , "value": f"http://ndtp.co.uk/data#UPRN_{uprn}" } ,
                "roofConstruction": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#RoofRooms" } ,
                "roofInsulation": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#InsulatedAssumed" },
                "roofInsulationThickness": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#250mm_Insulation" }
            }
            ]
        }
    }
    
def floor_query_response(uprn):
    return {
        "results": {
            "bindings": [
            { 
                "uprn": { "type": "uri" , "value": f"http://ndtp.co.uk/data#UPRN_{uprn}" } ,
                "floorConstruction": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#Suspended" } ,
                "floorInsulation": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#NoInsulationInFloor" }
            }
            ]
        }
    }
    
def wall_window_query_response(uprn):
    return {
        "results": {
            "bindings": [
            { 
                "uprn": { "type": "uri" , "value": f"http://ndtp.co.uk/data#UPRN_{uprn}" } ,
                "wallConstruction": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#CavityWall" } ,
                "wallInsulation": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#InsulatedWall" } ,
                "windowGlazing": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#DoubleGlazingBefore2002" }
            }
            ]
        }
    }

def empty_query_response():
    return {
        "results": {
            "bindings": []
        }
    }
    
def bounded_buildings_response():
    first = bounded_building_response(100060763456, "1 Apple Avenue", "osgb1000013062259", "POINT(-1.1834759844410794 50.72234886358317)", "C", "Bungalow")
    second = bounded_building_response(100060768637, "2 Orange Road", "osgb1000013076936", "POINT(-1.178467890878929 50.725098060722736)", "C", "House")
    return {
        "results": {
            "bindings": [first, second]
        }
    }
    
def bounded_buildings_response_two_forms():
    first = bounded_building_response(100060763456, "1 Apple Avenue", "osgb1000013062259", "POINT(-1.1834759844410794 50.72234886358317)", "C", "House")
    second = bounded_building_response(100060768638, "3a Cherry Street", "osgb1000013076936", "POINT(-1.178467890878929 50.725098060722736)", "D", "Maisonette")
    third = bounded_building_response(100060763456, "1 Apple Avenue", "osgb1000013062259", "POINT(-1.1834759844410794 50.72234886358317)", "C", "Bungalow")
    fourth = bounded_building_response(100060768638, "3a Cherry Street", "osgb1000013076936", "POINT(-1.178467890878929 50.725098060722736)", "D", "Flat")
    return {
        "results": {
            "bindings": [first, second, third, fourth]
        }
    }
    
def bounded_building_response(uprn, address, toid, point, epc_rating, structure_unit_type):
    return {
            "uprn": { "type": "uri" , "value": f"http://ndtp.co.uk/data#UPRN_{uprn}" } ,
            "firstLineOfAddress": { "type": "uri" , "value": address } ,
            "toid": { "type": "literal" , "value": toid } ,
            "point": { "type": "literal" , "datatype": "http://www.opengis.net/ont/geosparql#wktLiteral" , "value": point } ,
            "epcRating": { "type": "uri" , "value": epc_rating } ,
            "structureUnitType": { "type": "uri" , "value": f"http://ies.data.gov.uk/ontology/ies-building1#{structure_unit_type}" }
        }
    
def bounded_detailed_buildings_response():
    return {
        "results": {
            "bindings": [
                { 
                    "uprn": { "type": "uri" , "value": "http://ndtp.co.uk/data#UPRN_10003319738" } ,
                    "point": { "type": "literal" , "datatype": "http://www.opengis.net/ont/geosparql#wktLiteral" , "value": "POINT(-1.172860902466188 50.6485359929191)" } ,
                    "postcode": { "type": "literal" , "value": "PO36 9JA" } ,
                    "windowGlazing": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#DoubleGlazingBefore2002" } ,
                    "wallConstruction": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#CavityWall" } ,
                    "wallInsulation": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#InsulatedWall" } ,
                    "floorConstruction": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#Suspended" } ,
                    "floorInsulation": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#NoInsulationInFloor" }
                } ,
                { 
                    "uprn": { "type": "uri" , "value": "http://ndtp.co.uk/data#UPRN_100060763759" } ,
                    "point": { "type": "literal" , "datatype": "http://www.opengis.net/ont/geosparql#wktLiteral" , "value": "POINT(-1.1511959894263062 50.71876029182787)" } ,
                    "postcode": { "type": "literal" , "value": "PO33 1DG" } ,
                    "windowGlazing": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#DoubleGlazingAfter2002" } ,
                    "wallConstruction": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#CavityWall" } ,
                    "wallInsulation": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#InsulatedWall" } ,
                    "floorConstruction": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#Suspended" } ,
                    "floorInsulation": { "type": "uri" , "value": "http://ies.data.gov.uk/ontology/ies-building1#NoInsulationInFloor" }
                }
            ]
        }
    }
 
def flag_history_response(active):
    result = {
        "results": {
            "bindings": [
                {
                    "uprn": {"value": "12345"},
                    "flag": {"value": "http://ndtp.co.uk/data#flag1"},
                    "flagType": {"value": "http://ndtp.co.uk/data#InterestedInInvestigating"},
                    "retrofitterName": {"value": "John Doe"},
                    "flagDate": {"value": "http://iso.org/iso8601#2020-01-01T00:00:00"}
                }
            ]
        }
    }
    if not active:
        result["results"]["bindings"][0]["assessmentDate"] = {"value": "http://iso.org/iso8601#2020-01-02T00:00:00"}
        result["results"]["bindings"][0]["assessorName"] = {"value": "Jane Smith"}
        result["results"]["bindings"][0]["assessmentReason"] = {"value": "Reason1"}
    return result

def multiple_flag_history_response(active):
    return {
        "results": {
            "bindings": [
                {
                    "uprn": {"value": "12345"},
                    "flag": {"value": "http://ndtp.co.uk/data#flag1"},
                    "flagType": {"value": "http://ndtp.co.uk/data#InterestedInInvestigating"},
                    "retrofitterName": {"value": "Simon Smith"},
                    "flagDate": {"value": "http://iso.org/iso8601#2020-01-03T00:00:00"},
                    "assessmentDate": {"value": ""},
                    "assessorName": {"value": ""},
                    "assessmentReason": {"value": ""}
                },
                {
                    "uprn": {"value": "67890"},
                    "flag": {"value": "http://ndtp.co.uk/data#flag2"},
                    "flagType": {"value": "http://ndtp.co.uk/data#InterestedInInvestigating"},
                    "retrofitterName": {"value": "John Doe"},
                    "flagDate": {"value": "http://iso.org/iso8601#2020-01-01T00:00:00"},
                    "assessmentDate": {"value": "http://iso.org/iso8601#2020-01-02T00:00:00"},
                    "assessorName": {"value": "Jane Smith"},
                    "assessmentReason": {"value": "Reason1"}
                }
            ]
        }
    }
       
def statistics_response():
    return {
        "results": {
            "bindings": [
                { 
                    "wardName": { "type": "literal" , "value": "Bembridge" } ,
                    "EPC_Rating_A": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "0" } ,
                    "EPC_Rating_B": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "1" } ,
                    "EPC_Rating_C": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "11" } ,
                    "EPC_Rating_D": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "8" } ,
                    "EPC_Rating_E": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "0" } ,
                    "EPC_Rating_F": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "0" } ,
                    "EPC_Rating_G": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "0" } ,
                    "No_EPC_Rating": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "4" }
                } ,
                { 
                    "wardName": { "type": "literal" , "value": "Binstead & Fishbourne" } ,
                    "EPC_Rating_A": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "0" } ,
                    "EPC_Rating_B": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "2" } ,
                    "EPC_Rating_C": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "12" } ,
                    "EPC_Rating_D": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "6" } ,
                    "EPC_Rating_E": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "2" } ,
                    "EPC_Rating_F": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "0" } ,
                    "EPC_Rating_G": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "1" } ,
                    "No_EPC_Rating": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#integer" , "value": "1" }
                }
            ]
        }
    }

def mock_known_building(query, headers):
    uprn = 10023456789
    if query == get_building(uprn):
        return building_query_response(uprn)
    if query == get_roof_for_building(uprn):
        return roof_query_response(uprn)
    if query == get_floor_for_building(uprn):
        return floor_query_response(uprn)
    if query == get_walls_and_windows_for_building(uprn):
        return wall_window_query_response(uprn)
    else:
        return "default response"