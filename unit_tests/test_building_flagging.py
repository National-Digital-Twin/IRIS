# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import uuid
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.models.ies_models import EDH, ClassificationEmum, IesEntity
from api.routes import (
    InvalidateFlag,
    access_client,
    create_person_insert,
    router,
)

from query_response_mocks import empty_query_response, flag_history_response, multiple_flag_history_response


@pytest.fixture(autouse=True)
def set_identity_api_url(monkeypatch):
    # Set the environment variable for all tests.
    monkeypatch.setenv("IDENTITY_API_URL", "https://test.com")


@pytest.fixture
def client():
    """Create a test client with the router mounted on a FastAPI app."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# Mock user data for testing
@pytest.fixture
def mock_user():
    return {
        "user_id": "test-user-123",
        "username": "Test User",
        "active": True,
        "email": "test.user@example.com",
        "attributes": {"role": "inspector"},
        "groups": ["building_inspectors"],
    }


# Test data: Entity to flag with fully qualified URI
@pytest.fixture
def entity_to_flag():
    return IesEntity(
        uri="http://ndtp.co.uk/data#building-123",  # Use full URI
        securityLabel=EDH(classification=ClassificationEmum.official),
    )


# Test data: Invalid flag data with fully qualified URI
@pytest.fixture
def invalid_flag_data():
    edh_instance = EDH(classification=ClassificationEmum.official)
    return InvalidateFlag(
        flagUri="http://ndtp.co.uk/data#flag-123",
        securityLabel=edh_instance.model_dump(),  # pass a dict instead of an instance
    )


# Common patching for run_sparql_update and access_client.get_user_details
@pytest.fixture
def setup_mocks(monkeypatch, mock_user):
    monkeypatch.setattr(uuid, "uuid4", lambda: "mocked-uuid")

    mock_datetime = MagicMock()
    mock_now = MagicMock()
    mock_now.return_value.isoformat.return_value = "2025-03-05T12:00:00"
    mock_datetime.now = mock_now

    datetime_patch = patch("api.routes.datetime", mock_datetime)
    datetime_patch.start()

    mock_get_user_details = MagicMock(return_value=mock_user)
    monkeypatch.setattr(access_client, "get_user_details", mock_get_user_details)

    mock_run_sparql_update = MagicMock()
    monkeypatch.setattr("api.routes.run_sparql_update", mock_run_sparql_update)

    yield {
        "mock_get_user_details": mock_get_user_details,
        "mock_run_sparql_update": mock_run_sparql_update,
    }

    datetime_patch.stop()


# Tests for flag-to-investigate endpoint
class TestFlagToInvestigate:
    def test_successful_flag_to_investigate(self, client, entity_to_flag, setup_mocks):
        """Test successful flagging of a building as 'to investigate'"""
        response = client.post(
            "/flag-to-investigate", json=entity_to_flag.model_dump(exclude_none=True)
        )

        assert response.status_code == 200
        assert response.json() == "http://ndtp.co.uk/data#mocked-uuid"

        setup_mocks["mock_get_user_details"].assert_called_once()

        setup_mocks["mock_run_sparql_update"].assert_called_once()
        call_args = setup_mocks["mock_run_sparql_update"].call_args[1]

        # Check the query contains the expected data
        assert "ndt:InterestedInInvestigating" in call_args["query"]
        assert (
            "http://ndtp.co.uk/data#mocked-uuid" in call_args["query"]
        )
        assert (
            "http://ndtp.co.uk/data#building-123" in call_args["query"]
        )
        assert "test-user-123" in call_args["query"]

    def test_missing_uri(self, client, setup_mocks):
        """Test that an error is raised when URI is missing"""
        invalid_entity = IesEntity(
            securityLabel=EDH(classification=ClassificationEmum.official)
        )

        response = client.post(
            "/flag-to-investigate", json=invalid_entity.model_dump(exclude_none=True)
        )

        assert response.status_code == 422
        assert "URI of flagged entity must be provided" in response.json()["detail"]

        setup_mocks["mock_run_sparql_update"].assert_not_called()

    def test_access_client_error_no_response(
        self, client, entity_to_flag, setup_mocks, monkeypatch
    ):
        """Test handling of access client errors when response is None"""
        # Create a RequestException with no response
        mock_exception = requests.exceptions.RequestException("Access client error")
        mock_exception.response = None

        mock_get_user = MagicMock(side_effect=mock_exception)
        monkeypatch.setattr(access_client, "get_user_details", mock_get_user)

        response = client.post(
            "/flag-to-investigate", json=entity_to_flag.model_dump(exclude_none=True)
        )

        assert response.status_code == 500
        assert (
            "Error calling Access, Internal Server Error" in response.json()["detail"]
        )

        setup_mocks["mock_run_sparql_update"].assert_not_called()


# Tests for invalidate-flag endpoint
class TestInvalidateFlag:
    def test_successful_invalidate_flag(
        self, client, invalid_flag_data, setup_mocks, monkeypatch
    ):
        """Test successful invalidation of a flag"""
        # Mock the get_subtypes function to return valid assessment classes
        mock_get_subtypes = MagicMock(
            return_value=(
                {
                    "http://ndtp.co.uk/ontology#AssessToBeFalse": {
                        "uri": "http://ndtp.co.uk/ontology#AssessToBeFalse",
                        "shortName": "ndt_ont:AssessToBeFalse",
                    }
                },
                [],
            )
        )
        monkeypatch.setattr("api.routes.get_subtypes", mock_get_subtypes)

        response = client.post(
            "/invalidate-flag", json=invalid_flag_data.model_dump(exclude_none=True)
        )

        assert response.status_code == 200
        assert response.json() == "http://ndtp.co.uk/data#mocked-uuid"

        setup_mocks["mock_run_sparql_update"].assert_called_once()
        call_args = setup_mocks["mock_run_sparql_update"].call_args[1]

        # Check the query contains the expected data
        assert "http://ndtp.co.uk/data#flag-123" in call_args["query"]
        assert "test-user-123" in call_args["query"]
        assert (
            "http://ndtp.co.uk/ontology#AssessToBeFalse"
            in call_args["query"]
        )

    def test_invalid_assessment_type(
        self, client, invalid_flag_data, setup_mocks, monkeypatch
    ):
        """Test error when the assessment type is invalid"""
        invalid_flag_data.assessmentTypeOverride = "ndt_ont:InvalidAssessmentType"

        mock_get_subtypes = MagicMock(return_value=({}, []))
        monkeypatch.setattr("api.routes.get_subtypes", mock_get_subtypes)

        response = client.post(
            "/invalidate-flag", json=invalid_flag_data.model_dump(exclude_none=True)
        )

        assert response.status_code == 422
        assert (
            "assessmentTypeOverride must be a subclass of ndt_ont:AssessToBeFalse"
            in response.json()["detail"]
        )

        setup_mocks["mock_run_sparql_update"].assert_not_called()

# Tests for retrieving flag history
class TestFlagHistory:
    def test_retrieve_only_active_flag(self, client, monkeypatch):
        mock_query = MagicMock(return_value=flag_history_response(True))
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        response = client.get("/buildings/12345/flag-history", headers={"dummy": "header"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["UPRN"] == "12345"
        assert data[0]["Flagged"] == "http://ndtp.co.uk/data#flag1"
        assert data[0]["FlagType"] == "InterestedInInvestigating"
        assert data[0]["FlaggedByName"] == "John Doe"
        assert data[0]["FlagDate"] == "2020-01-01T00:00:00"
        assert data[0]["AssessmentDate"] == ""
        assert data[0]["AssessorName"] == ""
        assert data[0]["AssessmentReason"] == ""
    
    def test_retrieve_only_historic_flag(self, client, monkeypatch):
        mock_query = MagicMock(return_value=flag_history_response(False))
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        response = client.get("/buildings/12345/flag-history", headers={"dummy": "header"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["UPRN"] == "12345"
        assert data[0]["Flagged"] == "http://ndtp.co.uk/data#flag1"
        assert data[0]["FlagType"] == "InterestedInInvestigating"
        assert data[0]["FlaggedByName"] == "John Doe"
        assert data[0]["FlagDate"] == "2020-01-01T00:00:00"
        assert data[0]["AssessmentDate"] == "2020-01-02T00:00:00"
        assert data[0]["AssessorName"] == "Jane Smith"
        assert data[0]["AssessmentReason"] == "Reason1"
    
    def test_retrieve_active_flag_with_historic_flag(self, client, monkeypatch):
        mock_query = MagicMock(return_value=multiple_flag_history_response(False))
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        response = client.get("/buildings/12345/flag-history", headers={"dummy": "header"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["UPRN"] == "12345"
        assert data[0]["Flagged"] == "http://ndtp.co.uk/data#flag1"
        assert data[0]["FlagType"] == "InterestedInInvestigating"
        assert data[0]["FlaggedByName"] == "Simon Smith"
        assert data[0]["FlagDate"] == "2020-01-03T00:00:00"
        assert data[0]["AssessmentDate"] == ""
        assert data[0]["AssessorName"] == ""
        assert data[0]["AssessmentReason"] == ""
        assert data[1]["UPRN"] == "67890"
        assert data[1]["Flagged"] == "http://ndtp.co.uk/data#flag2"
        assert data[1]["FlagType"] == "InterestedInInvestigating"
        assert data[1]["FlaggedByName"] == "John Doe"
        assert data[1]["FlagDate"] == "2020-01-01T00:00:00"
        assert data[1]["AssessmentDate"] == "2020-01-02T00:00:00"
        assert data[1]["AssessorName"] == "Jane Smith"
        assert data[1]["AssessmentReason"] == "Reason1"
        return
    
    def test_retrieve_no_flags(self, client, monkeypatch):
        mock_query = MagicMock(return_value=empty_query_response())
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        response = client.get("/buildings/12345/flag-history", headers={"dummy": "header"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

# Test helper functions
def test_create_person_insert():
    """Test the create_person_insert function that generates SPARQL for person creation"""
    user_id = "test-user-456"
    username = "John Doe"

    uri, person_sparql = create_person_insert(user_id, username)

    # Check the URI
    assert uri == "http://ndtp.co.uk/data#test-user-456"

    # Check the SPARQL query content
    assert "ies:Person" in person_sparql
    assert "John" in person_sparql
    assert "Doe" in person_sparql
    assert "ies:PersonName" in person_sparql
    assert "ies:GivenName" in person_sparql
    assert "ies:Surname" in person_sparql


if __name__ == "__main__":
    pytest.main(["-v", __file__])

