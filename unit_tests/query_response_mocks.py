from api.query import (
    get_building,
    get_floor_for_building,
    get_roof_for_building,
    get_walls_and_windows_for_building,
)


def building_query_response(uprn):
    return {
        "results": {
            "bindings": [
                {
                    "uprn": {
                        "type": "uri",
                        "value": f"http://ndtp.co.uk/data#UPRN_{uprn}",
                    },
                    "lodgementDate": {
                        "type": "uri",
                        "value": "http://iso8601.iso.org/2024-03-30",
                    },
                    "builtForm": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#SemiDetached",
                    },
                    "structureUnitType": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#House",
                    },
                }
            ]
        }
    }


def roof_query_response(uprn):
    return {
        "results": {
            "bindings": [
                {
                    "uprn": {
                        "type": "uri",
                        "value": f"http://ndtp.co.uk/data#UPRN_{uprn}",
                    },
                    "roofConstruction": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#RoofRooms",
                    },
                    "roofInsulation": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#InsulatedAssumed",
                    },
                    "roofInsulationThickness": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#250mm_Insulation",
                    },
                }
            ]
        }
    }


def floor_query_response(uprn):
    return {
        "results": {
            "bindings": [
                {
                    "uprn": {
                        "type": "uri",
                        "value": f"http://ndtp.co.uk/data#UPRN_{uprn}",
                    },
                    "floorConstruction": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#Suspended",
                    },
                    "floorInsulation": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#NoInsulationInFloor",
                    },
                }
            ]
        }
    }


def wall_window_query_response(uprn):
    return {
        "results": {
            "bindings": [
                {
                    "uprn": {
                        "type": "uri",
                        "value": f"http://ndtp.co.uk/data#UPRN_{uprn}",
                    },
                    "wallConstruction": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#CavityWall",
                    },
                    "wallInsulation": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#InsulatedWall",
                    },
                    "windowGlazing": {
                        "type": "uri",
                        "value": "http://ies.data.gov.uk/ontology/ies-building1#DoubleGlazingBefore2002",
                    },
                }
            ]
        }
    }


def empty_query_response():
    return {"results": {"bindings": []}}


def bounded_buildings_response():
    first = bounded_building_response(
        100060763456,
        "1 Apple Avenue",
        "osgb1000013062259",
        "POINT(-1.1834759844410794 50.72234886358317)",
        "C",
        "Bungalow",
    )
    second = bounded_building_response(
        100060768637,
        "2 Orange Road",
        "osgb1000013076936",
        "POINT(-1.178467890878929 50.725098060722736)",
        "C",
        "House",
    )
    return [first, second]


def bounded_buildings_response_two_forms():
    first = bounded_building_response(
        100060763456,
        "1 Apple Avenue",
        "osgb1000013062259",
        "POINT(-1.1834759844410794 50.72234886358317)",
        "C",
        "House",
    )
    second = bounded_building_response(
        100060768638,
        "3a Cherry Street",
        "osgb1000013076936",
        "POINT(-1.178467890878929 50.725098060722736)",
        "D",
        "Maisonette",
    )
    third = bounded_building_response(
        100060763456,
        "1 Apple Avenue",
        "osgb1000013062259",
        "POINT(-1.1834759844410794 50.72234886358317)",
        "C",
        "Bungalow",
    )
    fourth = bounded_building_response(
        100060768638,
        "3a Cherry Street",
        "osgb1000013076936",
        "POINT(-1.178467890878929 50.725098060722736)",
        "D",
        "Flat",
    )
    return [first, second, third, fourth]


def bounded_building_response(
    uprn, address, toid, point, epc_rating, structure_unit_type
):
    return {
        "uprn": uprn,
        "firstLineOfAddress": address,
        "toid": toid,
        "point": point,
        "epcRating": epc_rating,
        "structureUnitType": structure_unit_type,
    }


def bounded_filterable_buildings_response():
    return {
        [
            {
                "uprn": "10003319738",
                "postcode": "PO36 9JA",
                "built_form": "Detached",
                "lodgement_date": "2024-09-01",
                "fuel_type": "MainsGas",
                "window_glazing": "DoubleGlazingBefore2002",
                "wall_construction": "CavityWall",
                "wall_insulation": "InsulatedWall",
                "floor_construction": "Suspended",
                "floorInsulation": "NoInsulationInFloor",
                "roof_construction": "Pitched",
                "roof_insulation_location": "LoftInsulation",
                "roof_insulation_thickness": "100mm",
            },
            {
                "uprn": "100060763759",
                "postcode": "PO33 1DG",
                "built_form": "Detached",
                "lodgement_date": "2024-09-01",
                "fuel_type": "MainsGas",
                "window_glazing": "DoubleGlazingAfter2002",
                "wall_construction": "CavityWall",
                "wall_insulation": "InsulatedWall",
                "floor_construction": "Suspended",
                "floor_insulation": "NoInsulationInFloor",
                "roof_construction": "Pitched",
                "roof_insulation_location": "LoftInsulation",
                "roof_insulation_thickness": "100mm",
            },
        ]
    }


def flag_history_response(active):
    result = {
        "results": {
            "bindings": [
                {
                    "uprn": {"value": "12345"},
                    "flag": {"value": "http://ndtp.co.uk/data#flag1"},
                    "flagType": {
                        "value": "http://ndtp.co.uk/data#InterestedInInvestigating"
                    },
                    "retrofitterName": {"value": "John Doe"},
                    "flagDate": {"value": "http://iso.org/iso8601#2020-01-01T00:00:00"},
                }
            ]
        }
    }
    if not active:
        result["results"]["bindings"][0]["assessmentDate"] = {
            "value": "http://iso.org/iso8601#2020-01-02T00:00:00"
        }
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
                    "flagType": {
                        "value": "http://ndtp.co.uk/data#InterestedInInvestigating"
                    },
                    "retrofitterName": {"value": "Simon Smith"},
                    "flagDate": {"value": "http://iso.org/iso8601#2020-01-03T00:00:00"},
                    "assessmentDate": {"value": ""},
                    "assessorName": {"value": ""},
                    "assessmentReason": {"value": ""},
                },
                {
                    "uprn": {"value": "67890"},
                    "flag": {"value": "http://ndtp.co.uk/data#flag2"},
                    "flagType": {
                        "value": "http://ndtp.co.uk/data#InterestedInInvestigating"
                    },
                    "retrofitterName": {"value": "John Doe"},
                    "flagDate": {"value": "http://iso.org/iso8601#2020-01-01T00:00:00"},
                    "assessmentDate": {
                        "value": "http://iso.org/iso8601#2020-01-02T00:00:00"
                    },
                    "assessorName": {"value": "Jane Smith"},
                    "assessmentReason": {"value": "Reason1"},
                },
            ]
        }
    }


def statistics_response():
    return {
        "results": {
            "bindings": [
                {
                    "wardName": {"type": "literal", "value": "Bembridge"},
                    "EPC_Rating_A": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "0",
                    },
                    "EPC_Rating_B": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "1",
                    },
                    "EPC_Rating_C": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "11",
                    },
                    "EPC_Rating_D": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "8",
                    },
                    "EPC_Rating_E": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "0",
                    },
                    "EPC_Rating_F": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "0",
                    },
                    "EPC_Rating_G": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "0",
                    },
                    "No_EPC_Rating": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "4",
                    },
                },
                {
                    "wardName": {"type": "literal", "value": "Binstead & Fishbourne"},
                    "EPC_Rating_A": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "0",
                    },
                    "EPC_Rating_B": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "2",
                    },
                    "EPC_Rating_C": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "12",
                    },
                    "EPC_Rating_D": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "6",
                    },
                    "EPC_Rating_E": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "2",
                    },
                    "EPC_Rating_F": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "0",
                    },
                    "EPC_Rating_G": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "1",
                    },
                    "No_EPC_Rating": {
                        "type": "literal",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        "value": "1",
                    },
                },
            ]
        }
    }


def filter_summary_query_response():
    return {
        "postcode": ["P30", "P33"],
        "built_form": ["Detached", "SemiDetached"],
        "inspection_year": ["2024", "2020"],
        "energy_rating": ["In EPC"],
        "fuel_type": ["MainGas", "Oil", "Other"],
        "window_glazing": ["DoubleGlazing", "SecondaryGlazing", "TripleGlazing"],
        "wall_construction": ["CavityWall", "Cob", "Other"],
        "wall_insulation": ["AsBuilt", "FilledCavity"],
        "floor_construction": ["Solid", "Suspended", "Other"],
        "floor_insulation": ["Insulated", "NoInsulation"],
        "roof_construction": ["Pitched", "Flat", "RoofRooms"],
        "roof_insulation_location": [
            "LoftInsulation",
            "InsulationAtRafters",
            "InsulatedAssumed",
        ],
        "roof_insulation_thickness": ["100m", "200mm", "270mm"],
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

