# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import router
from unit_tests.query_response_mocks import statistics_response, empty_query_response

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

class TestGetEpcStatisticsForWards:
    def test_successful_get_statistics(self, client, monkeypatch):
        """Test successful retrieval of statistics"""
        mock_query = MagicMock(return_value=statistics_response())
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        
        response = client.get("/epc-statistics/wards")
        
        assert response.status_code == 200
        stats = response.json()
        
        assert len(stats) == 2
        assert stats[0]['b_rating'] == 1
        assert stats[0]['c_rating'] == 11
        assert stats[0]['d_rating'] == 8
        assert stats[0]['no_rating'] == 4
        mock_query.assert_called_once()
        
    def test_no_stats_found(self, client, monkeypatch):
        """Test successful retrieval of statistics"""
        mock_query = MagicMock(return_value=empty_query_response())
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        
        response = client.get("/epc-statistics/wards")
        
        assert response.status_code == 200
        stats = response.json()
        
        assert len(stats) == 0
        mock_query.assert_called_once()
        

if __name__ == "__main__":
    pytest.main(["-v", __file__])