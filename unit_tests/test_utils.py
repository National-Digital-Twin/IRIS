# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import pytest
from api.utils import validate_geojson_polygon


class TestValidateGeojsonPolygon:
    def test_valid_polygon(self):
        valid_polygon = '{"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}'
        validate_geojson_polygon(valid_polygon)

    def test_valid_multipolygon(self):
        valid_multipolygon = '{"type": "MultiPolygon", "coordinates": [[[[0, 0], [1, 0], [1, 1], [0, 0]]]]}'
        validate_geojson_polygon(valid_multipolygon)

    def test_invalid_json(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            validate_geojson_polygon("not valid json")

    def test_json_not_object(self):
        with pytest.raises(ValueError, match="GeoJSON must be a JSON object"):
            validate_geojson_polygon('["array", "not", "object"]')

    def test_missing_type_field(self):
        with pytest.raises(ValueError, match="GeoJSON must have a 'type' field"):
            validate_geojson_polygon('{"coordinates": [[0, 0]]}')

    def test_invalid_type(self):
        with pytest.raises(
            ValueError, match="GeoJSON type must be 'Polygon' or 'MultiPolygon'"
        ):
            validate_geojson_polygon('{"type": "InvalidType", "coordinates": [[0, 0]]}')

    def test_point_not_allowed(self):
        with pytest.raises(
            ValueError, match="GeoJSON type must be 'Polygon' or 'MultiPolygon'"
        ):
            validate_geojson_polygon('{"type": "Point", "coordinates": [0, 0]}')

    def test_linestring_not_allowed(self):
        with pytest.raises(
            ValueError, match="GeoJSON type must be 'Polygon' or 'MultiPolygon'"
        ):
            validate_geojson_polygon(
                '{"type": "LineString", "coordinates": [[0, 0], [1, 1]]}'
            )

    def test_missing_coordinates_field(self):
        with pytest.raises(ValueError, match="GeoJSON must have a 'coordinates' field"):
            validate_geojson_polygon('{"type": "Polygon"}')

    def test_coordinates_not_array(self):
        with pytest.raises(ValueError, match="GeoJSON 'coordinates' must be an array"):
            validate_geojson_polygon(
                '{"type": "Polygon", "coordinates": "not an array"}'
            )
