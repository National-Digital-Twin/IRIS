# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import datetime
import uuid
import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

# Import from your routes module (adjust path if needed)
import api.routes as routes

# --- Dummy classes and helper functions for testing ---

# Dummy class for IesThing (used by mint_uri)
class DummyIesThing:
    def __init__(self, uri=None, securityLabel=None):
        self.uri = uri
        self.securityLabel = securityLabel

# Dummy EDH-like object
class DummyEDH:
    def __init__(self, classification="official"):
        self.classification = classification

    def to_string(self):
        return self.classification

    def __eq__(self, other):
        if isinstance(other, DummyEDH):
            return self.classification == other.classification
        return False

# A dummy user to be returned by the access client
dummy_user = {"user_id": "user123", "username": "John Doe"}

# Dummy Request for calling plain functions
class DummyRequest:
    def __init__(self, headers=None):
        self.headers = headers or {}

# Override get_forwarding_headers to simply return the headers unchanged.
def dummy_get_forwarding_headers(headers):
    return headers

# Dummy RecordUtils so that get_headers (used in run_sparql_update) works.
class DummyRecordUtils:
    @staticmethod
    def to_headers(d):
        return d

# Dummy adapter for Kafka branch in run_sparql_update
class DummyAdapter:
    def send(self, record):
        self.last_record = record

# --- Fixtures for FastAPI endpoints ---
@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(routes.router)
    return TestClient(app)

# --- Tests for plain helper functions ---

def test_add_prefix():
    routes.prefix_dict.clear()
    routes.add_prefix("test", "http://example.com/")
    assert routes.prefix_dict["test"] == "http://example.com/"

def test_format_prefixes():
    routes.prefix_dict.clear()
    routes.add_prefix("ex", "http://example.com/")
    result = routes.format_prefixes()
    assert "PREFIX ex: <http://example.com/>" in result

def test_shorten_and_lengthen():
    routes.prefix_dict.clear()
    routes.add_prefix("ex", "http://example.com/")
    uri = "http://example.com/resource"
    short = routes.shorten(uri)
    assert short == "ex:resource"
    long_uri = routes.lengthen(short)
    assert long_uri == "http://example.com/resource"

def test_mint_uri():
    dummy = DummyIesThing()
    dummy.securityLabel = None
    result = routes.mint_uri(dummy)
    assert result.uri is not None
    assert result.uri.startswith(routes.data_uri_stub)
    assert result.securityLabel == routes.default_security_label

# --- Tests for functions that make HTTP calls ---

def test_run_sparql_query_success(monkeypatch):
    class DummyResponse:
        def __init__(self, json_data, status_code=200):
            self._json = json_data
            self.status_code = status_code
        def json(self):
            return self._json
        def raise_for_status(self):
            pass
    def dummy_get(url, params, headers):
        return DummyResponse({"results": {"bindings": []}})
    
    monkeypatch.setattr(routes.requests, "get", dummy_get)
    result = routes.run_sparql_query("query", {"header": "value"})
    assert result == {"results": {"bindings": []}}

def test_run_sparql_query_error(monkeypatch):
    class DummyResponse:
        def __init__(self, status_code):
            self.status_code = status_code
            self.reason = "error"
        def raise_for_status(self):
            raise routes.requests.exceptions.HTTPError(response=self)
    def dummy_get(url, params, headers):
        return DummyResponse(404)
    
    monkeypatch.setattr(routes.requests, "get", dummy_get)
    with pytest.raises(HTTPException) as excinfo:
        routes.run_sparql_query("query", {"header": "value"})
    assert excinfo.value.status_code == 404

def test_run_sparql_update_scg(monkeypatch):
    # Set update_mode to "SCG" to use that branch.
    routes.update_mode = "SCG"
    def dummy_post(url, headers, data):
        class DummyResponse:
            def raise_for_status(self):
                pass
        return DummyResponse()
    monkeypatch.setattr(routes.requests, "post", dummy_post)
    routes.run_sparql_update("query", {"fwd": "header"}, None)

def test_run_sparql_update_unknown(monkeypatch):
    routes.update_mode = "UNKNOWN"
    with pytest.raises(Exception) as excinfo:
        routes.run_sparql_update("query")
    assert "unknown update mode" in str(excinfo.value)
    routes.update_mode = "SCG"

# --- Tests for get_subtypes and create_person_insert ---

def test_get_subtypes_with_results(monkeypatch):
    dummy_result = {
        "results": {
            "bindings": [
                {
                    "sub": {"value": "http://example.com/sub1"},
                    "parent": {"value": "http://example.com/parent1"},
                    "comment": {"value": "dummy"}
                },
                {
                    "sub": {"value": "http://example.com/sub1"},
                    "parent": {"value": "http://example.com/parent2"}
                }
            ]
        }
    }
    monkeypatch.setattr(routes, "run_sparql_query", lambda q, h, query_dataset="ontology": dummy_result)
    sub_classes, sub_list = routes.get_subtypes("super_class", {"header": "value"}, "exclude")
    assert "http://example.com/sub1" in sub_classes
    # The description should include "dummy"
    assert "dummy" in sub_classes["http://example.com/sub1"]["description"]
    assert "http://example.com/parent1" in sub_classes["http://example.com/sub1"]["superClasses"]
    assert "http://example.com/parent2" in sub_classes["http://example.com/sub1"]["superClasses"]

def test_get_subtypes_no_results(monkeypatch):
    dummy_result = {"results": {"bindings": []}}
    monkeypatch.setattr(routes, "run_sparql_query", lambda q, h, query_dataset="ontology": dummy_result)
    sub_classes, sub_list = routes.get_subtypes("super_class", {"header": "value"})
    assert sub_classes == {}
    assert sub_list == []

def test_create_person_insert():
    uri, sparql = routes.create_person_insert("user123", "John Doe")
    expected_uri = routes.data_uri_stub + "user123"
    assert uri == expected_uri
    assert "<" + expected_uri + ">" in sparql
    assert "John" in sparql
    assert "Doe" in sparql

# --- Tests for API endpoints via TestClient ---

def test_test_user_passthrough(client, monkeypatch):
    monkeypatch.setattr(routes.access_client, "get_user_details", lambda headers: dummy_user)
    response = client.get("/test-user-passthrough", headers={"dummy": "header"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0] == dummy_user

def test_version_info(client):
    routes.config["metadata"] = {"version": "1.0"}
    response = client.get("/version-info")
    assert response.status_code == 200
    data = response.json()
    assert data == {"version": "1.0"}

def test_test_post(client):
    response = client.post("/test-post")
    assert response.status_code == 200

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_invalidate_flag_bad_assessment_type(client, monkeypatch):
    monkeypatch.setattr(routes.access_client, "get_user_details", lambda headers: dummy_user)
    monkeypatch.setattr(routes, "get_subtypes", lambda sc, h: ({}, []))
    payload = {
        "flagUri": "http://example.com/flag1",
        "assessmentTypeOverride": "invalid",
        "securityLabel": None
    }
    response = client.post("/invalidate-flag", json=payload, headers={"dummy": "header"})
    assert response.status_code == 422

def test_get_building_by_uprn(client, monkeypatch):
    dummy_result = {
        "results": {
            "bindings": [
                {
                    "building": {"value": "http://example.com/building1"},
                    "buildingType": {"value": "http://example.com/type1"},
                    "state": {"value": "http://example.com/state1"},
                    "stateType": {"value": "http://example.com/stateType1"},
                }
            ]
        }
    }
    monkeypatch.setattr(routes, "run_sparql_query", lambda q, h: dummy_result)
    response = client.get("/buildings/uprn123", headers={"dummy": "header"})
    assert response.status_code == 200
    data = response.json()
    assert data["entity"]["uri"] == "http://example.com/building1"
    assert "http://example.com/type1" in data["entity"]["types"]
    assert len(data["states"]) == 1

def test_get_building_flag_history(client, monkeypatch):
    dummy_result = {
        "results": {
            "bindings": [
                {
                    "UPRN": {"value": "12345"},
                    "Flagged": {"value": "http://example.com/flag1"},
                    "FlagType": {"value": "Type1"},
                    "FlaggedByGivenName": {"value": "John"},
                    "FlaggedBySurname": {"value": "Doe"},
                    "FlagDate": {"value": "2020-01-01T00:00:00"},
                    "AssessmentDate": {"value": "2020-01-02T00:00:00"},
                    "AssessorGivenName": {"value": "Jane"},
                    "AssessorSurname": {"value": "Smith"},
                    "AssessmentReason": {"value": "Reason1"}
                }
            ]
        }
    }
    monkeypatch.setattr(routes, "run_sparql_query", lambda q, h: dummy_result)
    response = client.get("/buildings/uprn123/flag-history", headers={"dummy": "header"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["UPRN"] == "12345"

def test_get_flagged_buildings(client, monkeypatch):
    dummy_result = {
        "results": {
            "bindings": [
                {
                    "UPRN": {"value": "12345"},
                    "TOID": {"value": "toid1"},
                    "ParentTOID": {"value": "pto1"},
                    "Flagged": {"value": "http://example.com/flag1"},
                    "FlagDate": {"value": "2020-01-01T00:00:00"}
                }
            ]
        }
    }
    monkeypatch.setattr(routes, "run_sparql_query", lambda q, h: dummy_result)
    response = client.get("/flagged-buildings", headers={"dummy": "header"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["UPRN"] == "12345"

def test_post_flag_visit(client, monkeypatch):
    monkeypatch.setattr(routes.access_client, "get_user_details", lambda headers: dummy_user)
    called = {}
    def dummy_run_sparql_update(query, forwarding_headers, securityLabel):
        called["query"] = query
    monkeypatch.setattr(routes, "run_sparql_update", dummy_run_sparql_update)
    class DummyIesEntity:
        def __init__(self, uri, securityLabel=None):
            self.uri = uri
            self.securityLabel = securityLabel
    dummy_entity = DummyIesEntity("http://example.com/entity")
    response = client.post("/flag-to-visit", json={"uri": dummy_entity.uri, "securityLabel": None}, headers={"dummy": "header"})
    assert response.status_code == 200
    flag_state = response.json()
    assert flag_state.startswith(routes.data_uri_stub)

def test_post_flag_investigate(client, monkeypatch):
    monkeypatch.setattr(routes.access_client, "get_user_details", lambda headers: dummy_user)
    called = {}
    def dummy_run_sparql_update(query, forwarding_headers, securityLabel):
        called["query"] = query
    monkeypatch.setattr(routes, "run_sparql_update", dummy_run_sparql_update)
    class DummyIesEntity:
        def __init__(self, uri, securityLabel=None):
            self.uri = uri
            self.securityLabel = securityLabel
    dummy_entity = DummyIesEntity("http://example.com/entity")
    response = client.post("/flag-to-investigate", json={"uri": dummy_entity.uri, "securityLabel": None}, headers={"dummy": "header"})
    assert response.status_code == 200
    flag_state = response.json()
    assert flag_state.startswith(routes.data_uri_stub)

# --- Tests for plain (non-endpoint) functions ---

def test_post_building_state(monkeypatch):
    class DummyIesState:
        def __init__(self, stateType, stateOf, startDateTime=None, endDateTime=None, securityLabel=None):
            self.uri = None
            self.stateType = stateType
            self.stateOf = stateOf
            self.startDateTime = startDateTime
            self.endDateTime = endDateTime
            self.securityLabel = securityLabel
    dummy_state = DummyIesState(
        "http://example.com/stateType",
        "http://example.com/stateOf",
        datetime.datetime(2020, 1, 1),
        datetime.datetime(2020, 1, 2),
        None,
    )
    routes.building_state_classes = {"http://example.com/stateType": {}}
    called = {}
    def dummy_run_sparql_update(query, securityLabel):
        called["query"] = query
    monkeypatch.setattr(routes, "run_sparql_update", dummy_run_sparql_update)
    uri = routes.post_building_state(dummy_state)
    assert dummy_state.uri.startswith(routes.data_uri_stub)
    assert "INSERT DATA" in called["query"]

def test_post_account(monkeypatch):
    class DummyIesAccount:
        def __init__(self, id, uri=None, email=None, name=None, securityLabel=None):
            self.id = id
            self.uri = uri
            self.email = email
            self.name = name
            self.securityLabel = securityLabel
    dummy_account = DummyIesAccount("acc123", None, "test@example.com", "Test Name", None)
    called = {}
    def dummy_run_sparql_update(query, securityLabel):
        called["query"] = query
    monkeypatch.setattr(routes, "run_sparql_update", dummy_run_sparql_update)
    uri = routes.post_account(dummy_account)
    assert uri.startswith(routes.data_uri_stub)
    assert "INSERT DATA" in called["query"]

def test_assess(monkeypatch):
    class DummyIesAssessment:
        def __init__(self, uri=None, inPeriod=None, assessor=None, types=None, assessedItem="item", securityLabel=None):
            self.uri = uri
            self.inPeriod = inPeriod
            self.assessor = assessor
            self.types = types or []
            self.assessedItem = assessedItem
            self.securityLabel = securityLabel
    dummy_assessment = DummyIesAssessment(types=["http://example.com/type1"])
    called = {}
    # Monkeypatch the datetime module reference so that datetime.datetime.now() works.
    monkeypatch.setattr(routes, "datetime", __import__("datetime"))
    def dummy_run_sparql_update(query, securityLabel):
        called["query"] = query
    monkeypatch.setattr(routes, "run_sparql_update", dummy_run_sparql_update)
    uri = routes.assess(dummy_assessment)
    assert uri.startswith(routes.data_uri_stub)
    assert "INSERT DATA" in called["query"]

def test_post_assess_to_be_true(monkeypatch):
    class DummyIesAssessToBeTrue:
        def __init__(self, uri=None, inPeriod=None, assessor=None, types=None, assessedItem="item", securityLabel=None):
            self.uri = uri
            self.inPeriod = inPeriod
            self.assessor = assessor
            self.types = types or ["http://example.com/type_true"]
            self.assessedItem = assessedItem
            self.securityLabel = securityLabel
    dummy_ass = DummyIesAssessToBeTrue()
    called = {}
    monkeypatch.setattr(routes, "datetime", __import__("datetime"))
    def dummy_run_sparql_update(query, securityLabel):
        called["query"] = query
    monkeypatch.setattr(routes, "run_sparql_update", dummy_run_sparql_update)
    uri = routes.post_assess_to_be_true(dummy_ass)
    assert uri.startswith(routes.data_uri_stub)
    assert "INSERT DATA" in called["query"]

def test_post_assess_to_be_false(monkeypatch):
    class DummyIesAssessToBeFalse:
        def __init__(self, uri=None, inPeriod=None, assessor=None, types=None, assessedItem="item", securityLabel=None):
            self.uri = uri
            self.inPeriod = inPeriod
            self.assessor = assessor
            self.types = types or ["http://example.com/type_false"]
            self.assessedItem = assessedItem
            self.securityLabel = securityLabel
    dummy_ass = DummyIesAssessToBeFalse()
    called = {}
    monkeypatch.setattr(routes, "datetime", __import__("datetime"))
    def dummy_run_sparql_update(query, securityLabel):
        called["query"] = query
    monkeypatch.setattr(routes, "run_sparql_update", dummy_run_sparql_update)
    uri = routes.post_assess_to_be_false(dummy_ass)
    assert uri.startswith(routes.data_uri_stub)
    assert "INSERT DATA" in called["query"]

def test_post_and_get_uri_stub(client):
    # post_uri_stub does a local assignment; the global data_uri_stub remains unchanged.
    response = client.post("/uri-stub", params={"uri": "http://newstub/"})
    assert response.status_code == 204
    response = client.get("/uri-stub")
    # get_uri_stub returns the global data_uri_stub.
    assert response.status_code == 200
    assert response.text.strip('"') == routes.data_uri_stub

def test_default_security_label(client):
    # Send a valid EDH value. Adjust according to your EDH model validation.
    payload = {"classification": "O"}
    response = client.post("/default-security-label", json=payload)
    assert response.status_code == 204
    response = client.get("/default-security-label")
    data = response.json()
    assert data.get("classification") == "O"

def test_post_assessment_error_no_assessed_item():
    class DummyIesAssessment:
        def __init__(self, uri=None, assessedItem="", assessmentType="class", userOverride=None,
                     startDate=datetime.datetime.now(), endDate=datetime.datetime.now(), securityLabel=None):
            self.uri = uri
            self.assessedItem = assessedItem
            self.assessmentType = assessmentType
            self.userOverride = userOverride
            self.startDate = startDate
            self.endDate = endDate
            self.securityLabel = securityLabel
    dummy_ass = DummyIesAssessment()
    with pytest.raises(HTTPException) as excinfo:
        routes.post_assessment(dummy_ass)
    assert excinfo.value.status_code == 400

def test_post_assessment_error_no_assessment_class():
    class DummyIesAssessment:
        def __init__(self, uri=None, assessedItem="item", assessmentType="", userOverride=None,
                     startDate=datetime.datetime.now(), endDate=datetime.datetime.now(), securityLabel=None):
            self.uri = uri
            self.assessedItem = assessedItem
            self.assessmentType = assessmentType
            self.userOverride = userOverride
            self.startDate = startDate
            self.endDate = endDate
            self.securityLabel = securityLabel
    dummy_ass = DummyIesAssessment()
    with pytest.raises(HTTPException) as excinfo:
        routes.post_assessment(dummy_ass)
    assert excinfo.value.status_code == 400

def test_post_assessment_not_found(monkeypatch):
    class DummyIesAssessment:
        def __init__(self, uri=None, assessedItem="item", assessmentType="not_found", userOverride=None,
                     startDate=datetime.datetime.now(), endDate=datetime.datetime.now(), securityLabel=None):
            self.uri = uri
            self.assessedItem = assessedItem
            self.assessmentType = assessmentType
            self.userOverride = userOverride
            self.startDate = startDate
            self.endDate = endDate
            self.securityLabel = securityLabel
    dummy_ass = DummyIesAssessment()
    routes.assessment_classes = {}
    monkeypatch.setattr(routes, "get_assessments", lambda: None)
    with pytest.raises(HTTPException) as excinfo:
        routes.post_assessment(dummy_ass)
    assert excinfo.value.status_code == 404
