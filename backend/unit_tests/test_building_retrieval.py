# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import math
from unittest.mock import ANY, AsyncMock, MagicMock, Mock

import db as db_module
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.query import (
    get_building,
    get_floor_for_building,
    get_fueltype_for_building,
    get_ngd_roof_aspect_areas_for_building,
    get_ngd_roof_material_for_building,
    get_ngd_roof_shape_for_building,
    get_ngd_solar_panel_presence_for_building,
    get_roof_for_building,
    get_walls_and_windows_for_building,
)
from api.routes import router
from unit_tests.query_response_mocks import empty_query_response, mock_known_building


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "TEST")


@pytest.fixture(autouse=True)
def set_identity_api_url(monkeypatch):
    # Set the environment variable for all tests.
    monkeypatch.setenv("IDENTITY_API_URL", "https://test.com")


@pytest.fixture
def test_app():
    mock_db_session = AsyncMock()

    async def mock_get_db():

        yield mock_db_session

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[db_module.get_db] = mock_get_db
    yield TestClient(app), mock_db_session

    app.dependency_overrides.clear()


class TestGetBuildingsInBoundingBox:
    def test_successful_get_buildings(self, test_app):
        """Test successful retrieval of buildings in a bounding box"""
        client, mock_db_session = test_app

        mock_db_result = AsyncMock()
        mock_db_result.__iter__ = lambda self: iter(
            [
                type(
                    "",
                    (object,),
                    {
                        "uprn": "100060763456",
                        "first_line_of_address": "1 Apple Avenue",
                        "epc_rating": "C",
                        "structure_unit_type": "Bungalow",
                        "toid": "osgb1000013062259",
                        "point": "0101000020e6100000d8698c8384eff2bf029ba5ed755c4940",
                    },
                ),
                type(
                    "",
                    (object,),
                    {
                        "uprn": "100060763457",
                        "first_line_of_address": "2 Apple Avenue",
                        "epc_rating": "B",
                        "structure_unit_type": "Bungalow",
                        "toid": "osgb1000013062269",
                        "point": "0101000020e610000081a2f5f851eff2bfc09857e5755c4940",
                    },
                ),
            ]
        )

        mock_db_session.execute.return_value = mock_db_result

        response = client.get(
            "/buildings?min_long=-1.1835&max_long=-1.1507&min_lat=50.6445&max_lat=50.7261"
        )

        assert response.status_code == 200
        buildings = response.json()

        assert len(buildings) == 2
        building = buildings[0]

        assert building["uprn"] == "100060763456"
        assert building["first_line_of_address"] == "1 Apple Avenue"
        assert building["energy_rating"] == "C"
        assert building["structure_unit_type"] == "Bungalow"
        assert building["toid"] == "osgb1000013062259"
        assert building["longitude"] == "-1.1834759844410794"
        assert building["latitude"] == "50.72234888635832"

    def test_empty_results(self, test_app):
        """Test when no buildings are found"""

        client, _ = test_app

        response = client.get(
            "/buildings?min_long=-1.1835&max_long=-1.1507&min_lat=50.6445&max_lat=50.7261"
        )

        assert response.status_code == 200
        buildings = response.json()
        assert len(buildings) == 0

    def verify_building_data(
        self,
        result,
        exp_uprn,
        exp_address,
        exp_epc,
        exp_type,
        exp_toid,
        exp_long,
        exp_lat,
    ):
        assert result["uprn"] == exp_uprn
        assert result["first_line_of_address"] == exp_address
        assert result["energy_rating"] == exp_epc
        assert result["structure_unit_type"] == exp_type
        assert result["toid"] == exp_toid
        assert result["longitude"] == exp_long
        assert result["latitude"] == exp_lat


class TestGetFilterableBuildingsInBoundingBox:
    def test_successful_get_buildings(self, test_app):
        """Test successful retrieval of filterable buildings in a bounding box"""

        client, mock_db_session = test_app

        mock_db_result = AsyncMock()
        mock_db_result.__iter__ = lambda self: iter(
            [
                type(
                    "",
                    (object,),
                    {
                        "uprn": "100000001165",
                        "post_code": "NE21 4DD",
                        "built_form": "MidTerrace",
                        "lodgement_date": "2009-04-06",
                        "fuel_type": "NaturalFuelGas",
                        "window_glazing": "DoubleGlazingBefore2002",
                        "wall_construction": "Sandstone",
                        "wall_insulation": "InsulatedWall",
                        "floor_construction": "Suspended",
                        "floor_insulation": "NoInsulationInFloor",
                        "roof_construction": "PitchedRoof",
                        "roof_insulation": "LoftInsulation",
                        "roof_insulation_thickness": "75mm",
                        "has_roof_solar_panels": "false",
                        "roof_material": "Tile Or Stone Or Slate",
                        "roof_aspect_area_facing_north_m2": 0,
                        "roof_aspect_area_facing_north_east_m2": 0,
                        "roof_aspect_area_facing_east_m2": 17.6,
                        "roof_aspect_area_facing_south_east_m2": 0,
                        "roof_aspect_area_facing_south_m2": 0,
                        "roof_aspect_area_facing_south_west_m2": 0,
                        "roof_aspect_area_facing_west_m2": 0,
                        "roof_aspect_area_facing_north_west_m2": 21.7,
                        "roof_aspect_area_indeterminable_m2": 0,
                        "roof_shape": "Pitched",
                    },
                ),
                type(
                    "",
                    (object,),
                    {
                        "uprn": "100000002463",
                        "post_code": "NE21 5RF",
                        "built_form": "SemiDetached",
                        "lodgement_date": "2025-02-04",
                        "fuel_type": "NaturalFuelGas",
                        "window_glazing": "DoubleGlazing",
                        "wall_construction": "SystemBuilt",
                        "wall_insulation": "ExternalInsulation",
                        "floor_construction": "SolidFloor",
                        "floor_insulation": "NoInsulationInFloor",
                        "roof_construction": "PitchedRoof",
                        "roof_insulation": "LoftInsulation",
                        "roof_insulation_thickness": "250mm",
                        "has_roof_solar_panels": "false",
                        "roof_material": "Tile Or Stone Or Slate",
                        "roof_aspect_area_facing_north_m2": 0,
                        "roof_aspect_area_facing_north_east_m2": 0,
                        "roof_aspect_area_facing_east_m2": 29.8,
                        "roof_aspect_area_facing_south_east_m2": 0,
                        "roof_aspect_area_facing_south_m2": 23,
                        "roof_aspect_area_facing_south_west_m2": 0,
                        "roof_aspect_area_facing_west_m2": 19.8,
                        "roof_aspect_area_facing_north_west_m2": 0,
                        "roof_aspect_area_indeterminable_m2": 2.2,
                        "roof_shape": "Pitched",
                    },
                ),
            ]
        )

        mock_db_session.execute.return_value = mock_db_result

        response = client.get(
            "/filterable-buildings?min_long=-1.1835&max_long=-1.1507&min_lat=50.6445&max_lat=50.7261"
        )

        assert response.status_code == 200
        buildings = response.json()

        assert len(buildings) == 2
        building = buildings[0]

        assert building["uprn"] == "100000001165"
        assert building["postcode"] == "NE21 4DD"
        assert building["built_form"] == "MidTerrace"
        assert building["lodgement_date"] == "2009-04-06"
        assert building["fuel_type"] == "NaturalFuelGas"
        assert building["window_glazing"] == "DoubleGlazingBefore2002"
        assert building["wall_construction"] == "Sandstone"
        assert building["wall_insulation"] == "InsulatedWall"
        assert building["floor_construction"] == "Suspended"
        assert building["floor_insulation"] == "NoInsulationInFloor"
        assert building["roof_construction"] == "PitchedRoof"
        assert building["roof_insulation_location"] == "LoftInsulation"
        assert building["roof_insulation_thickness"] == "75mm"
        assert building["has_roof_solar_panels"] is False
        assert building["roof_material"] == "TileOrStoneOrSlate"
        assert building["roof_aspect_area_facing_north"] == 0
        assert building["roof_aspect_area_facing_north_east"] == 0
        assert math.isclose(
            building["roof_aspect_area_facing_east"], 17.6, rel_tol=1e-09, abs_tol=1e-09
        )
        assert building["roof_aspect_area_facing_south_east"] == 0
        assert building["roof_aspect_area_facing_south"] == 0
        assert building["roof_aspect_area_facing_south_west"] == 0
        assert building["roof_aspect_area_facing_west"] == 0
        assert math.isclose(
            building["roof_aspect_area_facing_north_west"],
            21.7,
            rel_tol=1e-09,
            abs_tol=1e-09,
        )

    def test_empty_results(self, test_app):
        """Test when no buildings are found"""

        client, _ = test_app

        response = client.get(
            "/filterable-buildings?min_long=-1.1835&max_long=-1.1507&min_lat=50.6445&max_lat=50.7261"
        )

        assert response.status_code == 200
        buildings = response.json()
        assert len(buildings) == 0


class TestGetBuildingByUprn:
    def test_successful_get_building(self, test_app, monkeypatch):
        uprn = 10023456789
        mock_query = MagicMock()
        mock_query.side_effect = mock_known_building
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)

        client, _ = test_app

        response = client.get(f"/buildings/{uprn}")

        assert response.status_code == 200
        data = response.json()

        assert data["uprn"] == f"{uprn}"
        assert data["lodgement_date"] == "2024-03-30"
        assert data["built_form"] == "SemiDetached"
        assert data["structure_unit_type"] == "House"
        assert data["roof_construction"] == "RoofRooms"
        assert data["roof_insulation_location"] == "InsulatedAssumed"
        assert data["roof_insulation_thickness"] == "250mm_Insulation"
        assert data["floor_construction"] == "Suspended"
        assert data["floor_insulation"] == "NoInsulationInFloor"
        assert data["wall_construction"] == "CavityWall"
        assert data["wall_insulation"] == "InsulatedWall"
        assert data["window_glazing"] == "DoubleGlazingBefore2002"

        assert mock_query.call_count == 9
        mock_query.assert_any_call(get_building(uprn), ANY)
        mock_query.assert_any_call(get_roof_for_building(uprn), ANY)
        mock_query.assert_any_call(get_floor_for_building(uprn), ANY)
        mock_query.assert_any_call(get_walls_and_windows_for_building(uprn), ANY)
        mock_query.assert_any_call(get_fueltype_for_building(uprn), ANY)
        mock_query.assert_any_call(get_ngd_roof_material_for_building(uprn), ANY)
        mock_query.assert_any_call(get_ngd_solar_panel_presence_for_building(uprn), ANY)
        mock_query.assert_any_call(get_ngd_roof_shape_for_building(uprn), ANY)
        mock_query.assert_any_call(get_ngd_roof_aspect_areas_for_building(uprn), ANY)

    def test_building_not_found(self, test_app, monkeypatch):
        mock_query = MagicMock(return_value=empty_query_response())
        monkeypatch.setattr("api.routes.run_sparql_query", mock_query)
        uprn = 99999999999

        client, mock_db_session = test_app

        mock_db_result = Mock()
        mock_db_result.__iter__ = lambda self: iter([])
        mock_db_result.first.return_value = None
        mock_db_session.execute.return_value = mock_db_result

        response = client.get(f"/buildings/{uprn}")

        assert response.status_code == 200
        data = response.json()
        assert data["uprn"] == str(uprn)
        assert data["lodgement_date"] is None


if __name__ == "__main__":
    pytest.main(["-v", __file__])
