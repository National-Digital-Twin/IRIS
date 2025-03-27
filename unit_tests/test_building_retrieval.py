# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import router, run_sparql_query

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

# Mock SPARQL query results for building data
@pytest.fixture
def mock_building_query_results():
    return {
        "results": {
            "bindings": [
                {
                    "building": {"value": "http://nationaldigitaltwin.gov.uk/data#building123"},
                    "type": {"value": "http://ies.data.gov.uk/ontology/ies4#Building"},
                    "uprn_id": {"value": "10023456789"},
                    "current_energy_rating": {"value": "C"},
                    "flag": {"value": "http://nationaldigitaltwin.gov.uk/data#flag123"},
                    "flag_type": {"value": "http://nationaldigitaltwin.gov.uk/ontology#InterestedInVisiting"},
                    "flag_person": {"value": "http://nationaldigitaltwin.gov.uk/data#TestUser"},
                    "flag_date": {"value": "2025-02-01T10:00:00"},
                    "building_toid_id": {"value": "osgb1000012345678"}
                },
                {
                    "building": {"value": "http://nationaldigitaltwin.gov.uk/data#building123"},
                    "type": {"value": "http://nationaldigitaltwin.gov.uk/ontology#ResidentialBuilding"},
                    "uprn_id": {"value": "10023456789"},
                    "current_energy_rating": {"value": "C"},
                    "flag": {"value": "http://nationaldigitaltwin.gov.uk/data#flag456"},
                    "flag_type": {"value": "http://nationaldigitaltwin.gov.uk/ontology#InterestedInInvestigating"},
                    "flag_person": {"value": "http://nationaldigitaltwin.gov.uk/data#AnotherUser"},
                    "flag_date": {"value": "2025-02-15T14:30:00"},
                    "building_toid_id": {"value": "osgb1000012345678"}
                }
            ]
        }
    }

# Mock SPARQL query results for building by UPRN
@pytest.fixture
def mock_building_by_uprn_results():
    return {
        "results": {
            "bindings": [
                {
                    "building": {"value": "http://nationaldigitaltwin.gov.uk/data#building123"},
                    "buildingType": {"value": "http://ies.data.gov.uk/ontology/ies4#Building"},
                    "state": {"value": "http://nationaldigitaltwin.gov.uk/data#state123"},
                    "stateType": {"value": "http://gov.uk/government/organisations/department-for-levelling-up-housing-and-communities/ontology/epc#BuildingWithEnergyRatingOfC"}
                },
                {
                    "building": {"value": "http://nationaldigitaltwin.gov.uk/data#building123"},
                    "buildingType": {"value": "http://nationaldigitaltwin.gov.uk/ontology#ResidentialBuilding"},
                    "state": {"value": "http://nationaldigitaltwin.gov.uk/data#state456"},
                    "stateType": {"value": "http://nationaldigitaltwin.gov.uk/ontology#OccupiedState"}
                }
            ]
        }
    }

class TestGetBuildingsInGeohash:
    def test_successful_get_buildings(self, client, mock_building_query_results, monkeypatch):
        """Test successful retrieval of buildings in a geohash"""
        mock_query = MagicMock(return_value=mock_building_query_results)
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        
        response = client.get("/buildings?geohash=u10j7")
        
        assert response.status_code == 200
        buildings = response.json()
        
        assert len(buildings) == 1
        building = buildings[0]
        
        assert building["uri"] == "data:building123"
        assert building["uprn"] == "10023456789"
        assert building["currentEnergyRating"] == "C"
        assert building["buildingTOID"] == "osgb1000012345678"
        
        assert len(building["types"]) == 2
        assert "ies:Building" in building["types"]
        assert "ndt_ont:ResidentialBuilding" in building["types"]
        
        # Verify the flags
        assert len(building["flags"]) == 2
        assert "data:flag123" in building["flags"]
        assert "data:flag456" in building["flags"]
        
        flag123 = building["flags"]["data:flag123"]
        assert flag123["flagType"] == "ndt_ont:InterestedInVisiting"
        assert flag123["flaggedBy"] == "http://nationaldigitaltwin.gov.uk/data#TestUser"
        
        flag456 = building["flags"]["data:flag456"]
        assert flag456["flagType"] == "ndt_ont:InterestedInInvestigating"
        assert flag456["flaggedBy"] == "http://nationaldigitaltwin.gov.uk/data#AnotherUser"
        
        # Verify run_sparql_query was called with the correct params
        mock_query.assert_called_once()
        call_args = mock_query.call_args[0]
        assert "http://geohash.org/u10j7" in call_args[0]
    
    def test_empty_results(self, client, monkeypatch):
        """Test when no buildings are found"""
        # Mock the run_sparql_query function to return empty results
        empty_results = {"results": {"bindings": []}}
        mock_query = MagicMock(return_value=empty_results)
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        
        response = client.get("/buildings?geohash=u10j7")
        
        assert response.status_code == 200
        buildings = response.json()
        assert len(buildings) == 0

class TestGetBuildingByUprn:
    def test_successful_get_building(self, client, mock_building_by_uprn_results, monkeypatch):
        """Test successful retrieval of a building by UPRN"""
        # Mock the run_sparql_query function
        mock_query = MagicMock(return_value=mock_building_by_uprn_results)
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        
        response = client.get("/buildings/10023456789")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check the entity data
        entity = data["entity"]
        assert entity["uri"] == "http://nationaldigitaltwin.gov.uk/data#building123"
        assert len(entity["types"]) == 2
        assert "http://ies.data.gov.uk/ontology/ies4#Building" in entity["types"]
        assert "http://nationaldigitaltwin.gov.uk/ontology#ResidentialBuilding" in entity["types"]
        
        states = data["states"]
        assert len(states) == 2
        
        # Check the energy rating state
        energy_state = next(s for s in states if s["uri"] == "http://nationaldigitaltwin.gov.uk/data#state123")
        assert "http://gov.uk/government/organisations/department-for-levelling-up-housing-and-communities/ontology/epc#BuildingWithEnergyRatingOfC" in energy_state["types"]
        
        # Check the occupied state
        occupied_state = next(s for s in states if s["uri"] == "http://nationaldigitaltwin.gov.uk/data#state456")
        assert "http://nationaldigitaltwin.gov.uk/ontology#OccupiedState" in occupied_state["types"]
        
        # Verify run_sparql_query was called with the correct params
        mock_query.assert_called_once()
        call_args = mock_query.call_args[0]
        assert '10023456789' in call_args[0]
    
    def test_building_not_found(self, client, monkeypatch):
        """Test when building is not found"""
        # Mock the run_sparql_query function to return empty results
        empty_results = {"results": {"bindings": []}}
        mock_query = MagicMock(return_value=empty_results)
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        
        response = client.get("/buildings/99999999999")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check the response structure
        assert data["entity"]["uri"] == ""
        assert len(data["entity"]["types"]) == 0
        assert len(data["states"]) == 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])