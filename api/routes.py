# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import configparser
import os
import uuid
from datetime import datetime
from typing import List

import requests
from access import AccessClient
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
from models import (
    EDH,
    Building,
    ClassificationEmum,
    IesAccount,
    IesAssessment,
    IesAssessToBeFalse,
    IesAssessToBeTrue,
    IesClass,
    IesEntity,
    IesEntityAndStates,
    IesPerson,
    IesState,
    IesThing,
    ies,
)
from pydantic import BaseModel
from rdflib import Graph
from requests import exceptions
from utils import get_headers as get_forwarding_headers

load_dotenv()

router = APIRouter()

# If you're running this yourself, and the Jena instance you're using is not local, you can used environment variables to override
jenaURL = os.getenv("JENA_URL", "localhost")
jenaPort = os.getenv("JENA_PORT", "3030")
jenaProtocol = os.getenv("JENA_PROTOCOL", "http")
ontoDataset = os.getenv("ONTO_DATASET", "ontology")
dataset = os.getenv("KNOWLEDGE_DATASET", "knowledge")
default_security_label = EDH(classification=ClassificationEmum.official)
data_uri_stub = os.getenv(
    "DATA_URI", "http://nationaldigitaltwin.gov.uk/data#"
)  # This can be overridden in use
update_mode = os.getenv("UPDATE_MODE", "SCG")
access_protocol = os.getenv("ACCESS_PROTOCOL", "http")
access_host = os.getenv("ACCESS_URL", "localhost")
access_port = os.getenv("ACCESS_PORT", "8091")
dev_mode = os.getenv("DEV", "False")
access_path = os.getenv("ACCESS_PATH", "/")
identity_api_url = os.getenv("IDENTITY_API_URL", "http://localhost:3000/api")
landing_page_url = os.getenv("LANDING_PAGE_URL", "http://localhost:5173")

broker = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
fpTopic = os.getenv("IES_TOPIC", "knowledge")

ACCESS_API_CALL_ERROR = "Error calling Access, Internal Server Error"
ISO_8601_URL = "http://iso.org/iso8601#"

if update_mode == "KAFKA":
    from telicent_lib import Adapter, Record, RecordUtils
    from telicent_lib.sinks import KafkaSink

    knowledgeSink = KafkaSink(topic=fpTopic, broker=broker)
    knowledgeAdapter = Adapter(
        knowledgeSink, name="IoW Write-Back API", source_name="local data"
    )


def get_headers(security_labels):
    return RecordUtils.to_headers(
        {"Security-Label": security_labels, "Content-Type": "application/n-triples"}
    )


config = configparser.ConfigParser()
config.read("setup.cfg")
if dev_mode.lower() == "true":
    dev_mode = True
else:
    dev_mode = False
# The URIs used in the ontologies
ndt_ont = "http://nationaldigitaltwin.gov.uk/ontology#"

access_url = f"{access_protocol}://{access_host}:{access_port}{access_path}"
jena_url = f"{jenaProtocol}://{jenaURL}:{jenaPort}"


def add_prefix(prefix, uri):
    prefix_dict[prefix] = uri


access_client = AccessClient(access_url, dev_mode)
prefix_dict = {}
add_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")
add_prefix("dc", "http://purl.org/dc/elements/1.1/")
add_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
add_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
add_prefix("owl", "http://www.w3.org/2002/07/owl#")
add_prefix("ies", ies)
add_prefix("data", data_uri_stub)
add_prefix("ndt_ont", ndt_ont)
add_prefix("ndt", "http://nationaldigitaltwin.gov.uk/data#")
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


def run_sparql_query(query: str, headers: dict[str, str], query_dataset=dataset):
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
    query: str, forwarding_headers: dict[str, str] = {}, securityLabel=None
):
    global jena_url, default_security_label
    sec_label = securityLabel

    if sec_label is None:
        sec_label = default_security_label
    if update_mode == "SCG":
        post_uri = jena_url + "/" + dataset + "/update"
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
    elif update_mode == "KAFKA":
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
        raise ValueError("unknown update mode: " + update_mode)


def get_subtypes(super_class, headers: dict[str, str], exclude_super=None):
    sub_classes = {}
    sub_list = []
    if exclude_super is not None and exclude_super != "":
        filter_clause = (
            f"""FILTER NOT EXISTS {{ ?sub rdfs:subClassOf* <{exclude_super}>  }}  """
        )
    else:
        filter_clause = """"""
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
        query_dataset=ontoDataset,
    )

    if results and results["results"] and results["results"]["bindings"]:
        for sub in results["results"]["bindings"]:
            sub_uri = sub["sub"]["value"]
            if sub_uri not in sub_classes:
                # create a new empty(ish) item
                my_obj = {
                    "uri": sub_uri,
                    "shortName": shorten(sub_uri),
                    "superClasses": [],
                    "description": [],
                }
                sub_classes[sub_uri] = my_obj
            else:
                my_obj = sub_classes[sub_uri]
            # If there are any comments, append them
            if (
                "comment" in sub
                and sub["comment"]["value"]
                not in sub_classes[sub["sub"]["value"]]["description"]
            ):
                sub_classes[sub_uri]["description"].append(sub["comment"]["value"])
            # There may be more than one parent, so append them as we find them
            if sub["parent"]["value"] not in my_obj["superClasses"]:
                my_obj["superClasses"].append(sub["parent"]["value"])

    sub_list = []
    for key in sub_classes:
        sub = sub_classes[key]
        sub_list.append(
            {
                "uri": key,
                "shortName": sub["shortName"],
                "superClasses": sub["superClasses"],
                "description": sub["description"],
            }
        )

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
    run_sparql_update(query=query, securityLabel=per.securityLabel)
    return per.uri


@router.get(
    "/buildings",
    response_model=List[Building],
    description="Gets all the buildings inside a geohash (min 5 digits) along with their types, TOIDs, UPRNs, and current energy ratings",
)
def get_buildings_in_geohash(geohash: str, req: Request):
    if len(geohash) < 5:
        raise HTTPException(
            422, detail="Lat Lon range too wide, please provide at least five digits"
        )
    gh = "http://geohash.org/" + geohash

    query = f"""
        {format_prefixes()}
        SELECT
            ?building
            ?uprn_id
            ?building_toid_id
            ?parent_building_toid_id
            ?current_energy_rating
            ?parent_building
            ?type
            ?flag
            ?flag_type
            ?flag_person
            ?flag_date
            ?flag_assessment
            ?flag_ass_date
            ?flag_assessor
        WHERE {{
            ?building ies:inLocation ?geopoint .
            BIND(str(?geopoint) as ?gh) .
            FILTER (STRSTARTS(?gh,"{gh}") )
            ?building a ?type .

            ?state ies:isStateOf ?building .
            ?state a ?energy_rating .
            BIND(REPLACE(str(?energy_rating),"http://gov.uk/government/organisations/department-for-levelling-up-housing-and-communities/ontology/epc#BuildingWithEnergyRatingOf","","i") as ?current_energy_rating)

            ?building ies:isIdentifiedBy ?uprn .
            ?uprn ies:representationValue ?uprn_id .
            ?uprn rdf:type gp:UniquePropertyReferenceNumber .

            OPTIONAL {{
                ?flag ies:interestedIn ?building .
                ?flag ies:isStateOf ?flag_person .
                ?flag a ?flag_type .
                ?flag ies:inPeriod ?flag_date .
                OPTIONAL {{
                    ?flag_assessment ies:assessed ?flag .
                    ?flag_assessment ies:inPeriod ?flag_ass_date .
                    ?flag_assessment ies:assessor ?flag_assessor .
                }}
            }}

            OPTIONAL {{
                ?building ies:isIdentifiedBy ?building_toid .
                ?building_toid rdf:type ies:TOID .
                ?building_toid ies:representationValue ?building_toid_id .
            }}
            OPTIONAL {{
                ?building ies:isPartOf ?parent_building .
                ?parent_building ies:isIdentifiedBy ?parent_building_toid .
                ?parent_building_toid ies:representationValue ?parent_building_toid_id .
                ?parent_building_toid rdf:type ies:TOID .
            }}

        }}
    """

    out = {}
    out_array = []
    results = run_sparql_query(query, get_forwarding_headers(req.headers))

    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            building = shorten(result["building"]["value"])
            typ = shorten(result["type"]["value"])
            if building in out:
                building_obj = out[building]
                if typ not in building_obj["types"]:
                    building_obj["types"].append(typ)
            else:
                energy_rating = result["current_energy_rating"]["value"]
                building_obj = {
                    "uri": building,
                    "uprn": result["uprn_id"]["value"],
                    "currentEnergyRating": energy_rating,
                    "types": [typ],
                    "flags": {},
                    "invalidatedFlags": [],
                }
                out[building] = building_obj
                out_array.append(building_obj)

            if "flag" in result:
                flag = shorten(result["flag"]["value"])
                if flag not in building_obj["flags"]:
                    flag_obj = {
                        "flagType": shorten(result["flag_type"]["value"]),
                        "flaggedBy": result["flag_person"]["value"],
                        "date": result["flag_date"]["value"],
                    }
                    building_obj["flags"][flag] = flag_obj
                else:
                    flag_obj = building_obj["flags"][flag]
                if "flag_assessment" in result:
                    flag_obj["invalidated"] = result["flag_ass_date"]["value"]
                    flag_obj["invalidatedBy"] = result["flag_assessor"]["value"]

            if "building_toid_id" in result:
                building_obj["buildingTOID"] = result["building_toid_id"]["value"]
            elif "parent_building_toid_id" in result:
                building_obj["parentBuildingTOID"] = result["parent_building_toid_id"][
                    "value"
                ]

    return out_array


class InvalidateFlag(BaseModel):
    flagUri: str
    assessmentTypeOverride: str = prefix_dict["ndt_ont"] + "AssessToBeFalse"
    securityLabel: EDH = None


@router.post(
    "/invalidate-flag",
    description="Post to this endpoint to invalidate an existing flag.",
    response_model=str,
)
def invalidate_flag(request: Request, invalid: InvalidateFlag):
    try:
        user = access_client.get_user_details(request.headers)
    except exceptions.RequestException as e:
        if e.response is not None:
            raise HTTPException(
                e.response.status_code, f"Error calling Access:{e.response.reason}"
            )
        else:
            raise HTTPException(500, ACCESS_API_CALL_ERROR)
    assessor, person = create_person_insert(user["user_id"], user["username"])
    assessment_time = ISO_8601_URL + datetime.now().isoformat()
    assessment = data_uri_stub + str(uuid.uuid4())
    (assessment_subclasses, assessment_list) = get_subtypes(
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
    run_sparql_update(query=query, securityLabel=invalid.securityLabel)
    return assessment


@router.get(
    "/buildings/{uprn}",
    response_model=IesEntityAndStates,
    description="returns the building that corresponds to the provided UPRN",
)
def get_building_by_uprn(uprn: str, req: Request):
    query = f"""SELECT ?building ?buildingType ?state ?stateType WHERE
                {{
                    ?building ies:isIdentifiedBy ?uprnID .
                    ?building rdf:type ?buildingType .
                    ?uprnID ies:representationValue "{uprn}" .
                    OPTIONAL {{
                        ?state ies:isStateOf ?building .
                        ?state rdf:type ?stateType .
                    }}
                }}
            """
    results = run_sparql_query(query, get_forwarding_headers(req.headers))
    building = {
        "uri": "",
        "types": [],
    }
    states = {}
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            building["uri"] = result["building"]["value"]
            if result["buildingType"]["value"] not in building["types"]:
                building["types"].append(result["buildingType"]["value"])
            if result["state"]["value"]:
                state = result["state"]["value"]
                state_type = result["stateType"]["value"]
                if state not in states:
                    states[state] = {
                        "uri": state,
                        "types": [],
                        "stateOf": building["uri"],
                    }
                if state_type not in states[state]["types"]:
                    states[state]["types"].append(state_type)
    out = {"entity": building, "states": []}
    for state in states:
        out["states"].append(states[state])
    return out


@router.get(
    "/buildings/{uprn}/flag-history",
    description="Gets the flagging and assessment history for a specific building identified by its UPRN",
)
def get_building_flag_history(uprn: str, req: Request):
    query = f"""
        PREFIX data: <http://nationaldigitaltwin.gov.uk/data#>
        PREFIX ies: <http://ies.data.gov.uk/ontology/ies4#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT
            (REPLACE(STR(?uprn), "http://nationaldigitaltwin.gov.uk/data#uprn_", "") as ?UPRN)
            (?flag as ?Flagged)
            (REPLACE(STR(?flag_type), "http://nationaldigitaltwin.gov.uk/data#", "") as ?FlagType)
            (?given_name_literal AS ?FlaggedByGivenName)
            (?surname_literal AS ?FlaggedBySurname)
            (REPLACE(STR(?flag_date), "http://iso.org/iso8601#", "") as ?FlagDate)
            (REPLACE(STR(?flag_ass_date), "http://iso.org/iso8601#", "") AS ?AssessmentDate)
            (?assessor_given_name_literal AS ?AssessorGivenName)
            (?assessor_surname_literal AS ?AssessorSurname)
            (REPLACE(STR(?flag_assessment_type), "http://nationaldigitaltwin.gov.uk/ontology#", "") as ?AssessmentReason)
        WHERE {{
            ?building ies:isIdentifiedBy ?uprn .
            ?uprn ies:representationValue "{uprn}" .
            ?flag ies:interestedIn ?building .
            OPTIONAL {{
                ?flag ies:isStateOf ?flag_person .
                ?flag_person ies:hasName ?flag_person_name .
                ?surname a ies:Surname .
                ?surname ies:inRepresentation ?flag_person_name .
                ?surname ies:representationValue ?surname_literal .
                ?given_name a ies:GivenName .
                ?given_name ies:inRepresentation ?flag_person_name .
                ?given_name ies:representationValue ?given_name_literal .
                ?flag a ?flag_type .
                ?flag ies:inPeriod ?flag_date .
                OPTIONAL {{
                    ?flag_assessment ies:assessed ?flag .
                    ?flag_assessment ies:inPeriod ?flag_ass_date .
                    ?flag_assessment ies:assessor ?flag_assessor .
                    ?flag_assessor ies:hasName ?flag_assessor_name .
                    ?surname ies:inRepresentation ?flag_assessor_name .
                    ?surname ies:representationValue ?assessor_surname_literal .
                    ?given_name ies:inRepresentation ?flag_assessor_name .
                    ?given_name ies:representationValue ?assessor_given_name_literal .
                    ?flag_assessment rdf:type ?flag_assessment_type .
                }}
            }}
        }}
        GROUP BY
            ?flag
            ?flag_type
            ?flag_person
            ?flag_assessment
            ?flag_date
            ?flag_ass_date
            ?flag_assessor
            ?flag_assessment_type
            ?surname_literal
            ?given_name_literal
            ?assessor_given_name_literal
            ?assessor_surname_literal
            ?uprn
    """

    results = run_sparql_query(query, get_forwarding_headers(req.headers))

    flag_history = []
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            history_item = {
                "UPRN": result["UPRN"]["value"] if "UPRN" in result else uprn,
                "Flagged": result["Flagged"]["value"] if "Flagged" in result else None,
                "FlagType": (
                    result["FlagType"]["value"] if "FlagType" in result else None
                ),
                "FlaggedByGivenName": (
                    result["FlaggedByGivenName"]["value"]
                    if "FlaggedByGivenName" in result
                    else None
                ),
                "FlaggedBySurname": (
                    result["FlaggedBySurname"]["value"]
                    if "FlaggedBySurname" in result
                    else None
                ),
                "FlagDate": (
                    result["FlagDate"]["value"] if "FlagDate" in result else None
                ),
                "AssessmentDate": (
                    result["AssessmentDate"]["value"]
                    if "AssessmentDate" in result
                    else None
                ),
                "AssessorGivenName": (
                    result["AssessorGivenName"]["value"]
                    if "AssessorGivenName" in result
                    else None
                ),
                "AssessorSurname": (
                    result["AssessorSurname"]["value"]
                    if "AssessorSurname" in result
                    else None
                ),
                "AssessmentReason": (
                    result["AssessmentReason"]["value"]
                    if "AssessmentReason" in result
                    else None
                ),
            }
            flag_history.append(history_item)

    return flag_history


@router.get(
    "/flagged-buildings", description="Gets all buildings that have been flagged"
)
def get_flagged_buildings(req: Request):
    query = """
        PREFIX data: <http://nationaldigitaltwin.gov.uk/data#>
        PREFIX ies: <http://ies.data.gov.uk/ontology/ies4#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX gp: <https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn#>

        SELECT
            (REPLACE(STR(?uprn), "http://nationaldigitaltwin.gov.uk/data#uprn_", "") as ?UPRN)
            (?building_toid_id AS ?TOID)
            (?parent_building_toid_id AS ?ParentTOID)
            (?flag as ?Flagged)
            (REPLACE(STR(?flag_date), "http://iso.org/iso8601#", "") as ?FlagDate)
        WHERE {{
            ?state ies:isStateOf ?building .

            ?building ies:isIdentifiedBy ?uprn .
            ?uprn ies:representationValue ?uprn_id .
            ?uprn rdf:type gp:UniquePropertyReferenceNumber .

            ?flag ies:interestedIn ?building .
            FILTER NOT EXISTS {{ ?flag_assessment ies:assessed ?flag . }}

            OPTIONAL {{
                ?building ies:isIdentifiedBy ?building_toid .
                ?building_toid rdf:type ies:TOID .
                ?building_toid ies:representationValue ?building_toid_id .
            }}

            OPTIONAL {{
                ?building ies:isPartOf ?parent_building .
                ?parent_building ies:isIdentifiedBy ?parent_building_toid .
                ?parent_building_toid ies:representationValue ?parent_building_toid_id .
                ?parent_building_toid rdf:type ies:TOID .
            }}

            OPTIONAL {{
                ?flag ies:inPeriod ?flag_date .
            }}
        }}
        GROUP BY
            ?flag
            ?flag_date
            ?building_toid_id
            ?parent_building_toid_id
            ?uprn
    """

    results = run_sparql_query(query, get_forwarding_headers(req.headers))

    response_data = []
    if results and results["results"] and results["results"]["bindings"]:
        for result in results["results"]["bindings"]:
            flag_data = {
                "UPRN": result["UPRN"]["value"] if "UPRN" in result else None,
                "TOID": result["TOID"]["value"] if "TOID" in result else None,
                "ParentTOID": (
                    result["ParentTOID"]["value"] if "ParentTOID" in result else None
                ),
                "Flagged": result["Flagged"]["value"],
                "FlagDate": (
                    result["FlagDate"]["value"] if "FlagDate" in result else None
                ),
            }
            response_data.append(flag_data)

    return response_data


@router.post(
    "/flag-to-investigate",
    description="Add a flag to an Entity instance as being worth investigating- URI of Entity must be provided",
    response_model=str,
)
def post_flag_investigate(request: Request, visited: IesEntity):
    if not visited or not visited.uri:
        raise HTTPException(422, "URI of flagged entity must be provided")
    try:
        user = access_client.get_user_details(request.headers)
    except exceptions.RequestException as e:
        if e.response is not None:
            raise HTTPException(
                e.response.status_code, f"Error calling Access:{e.response.reason}"
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
        securityLabel=visited.securityLabel,
    )
    return flag_state


# @app.post("/buildings/states",description="Add a new state to a building")
def post_building_state(bs: IesState):
    if bs.stateType not in building_state_classes:
        # get_building_states()
        if bs.stateType not in building_state_classes:
            raise HTTPException(
                status_code=404,
                detail="Building State Class: " + bs.stateType + " not found",
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
    run_sparql_update(query=query, securityLabel=bs.securityLabel)
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
    run_sparql_update(query=query, securityLabel=acc.securityLabel)
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
    run_sparql_update(query=query, securityLabel=ass.securityLabel)

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
    data_uri_stub = uri  # noqa: F841
    return data_uri_stub


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
            raise HTTPException(
                status_code=404,
                detail="Assessment Class: " + ass.assessmentType + " not found",
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
            run_sparql_update(query=query, securityLabel=ass.securityLabel)

            return ass.uri
    raise HTTPException(status_code=400, detail="Could not create assessment")


@router.get("/user-details")
def get_user_details(request: Request):
    if dev_mode:
        return {
            "content": {"email": "local.user@test.com", "displayName": "Local User"}
        }

    user_details_response = requests.get(
        f"{identity_api_url}/v1/user-details", headers=request.headers
    )
    return user_details_response.json()


@router.get("/signout-links")
def get_signout_links():
    signout_links_response = requests.get(f"{identity_api_url}/v1/links/sign-out")
    if signout_links_response.status_code == 200:
        return {
            "oauth2Signout": f"{landing_page_url}/oauth2/signout",
            "signoutLink": signout_links_response.json(),
        }
    else:
        return f"Error {signout_links_response.status_code}: {signout_links_response.json()}"
