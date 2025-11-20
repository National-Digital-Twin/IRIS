# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import pytest
from api.utils import (
    validate_geojson_polygon,
    is_welsh_region,
    expand_wales_region,
    collapse_welsh_regions,
    WELSH_REGIONS,
)


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


class TestIsWelshRegion:
    def test_identifies_welsh_regions(self):
        """Test that all Welsh regions are correctly identified."""
        for region in WELSH_REGIONS:
            assert is_welsh_region(region) is True

    def test_rejects_english_regions(self):
        """Test that English regions are not identified as Welsh."""
        english_regions = [
            "London English Region",
            "North East English Region",
            "South East English Region",
        ]
        for region in english_regions:
            assert is_welsh_region(region) is False

    def test_rejects_invalid_names(self):
        """Test that invalid region names are not identified as Welsh."""
        assert is_welsh_region("Invalid Region") is False
        assert is_welsh_region("") is False
        assert is_welsh_region("Wales") is False


class TestExpandWalesRegion:
    def test_expands_wales_to_all_regions(self):
        """Test that 'Wales' is expanded to all 5 Welsh regions."""
        result = expand_wales_region(["Wales"])
        assert len(result) == 5
        assert set(result) == WELSH_REGIONS

    def test_expands_wales_with_other_regions(self):
        """Test that 'Wales' is expanded while keeping other regions."""
        result = expand_wales_region(["Wales", "London English Region"])
        assert len(result) == 6
        assert "London English Region" in result
        assert "Wales" not in result
        assert all(region in result for region in WELSH_REGIONS)

    def test_passes_through_non_wales_regions(self):
        """Test that non-Wales regions are passed through unchanged."""
        input_regions = ["London English Region", "North East English Region"]
        result = expand_wales_region(input_regions)
        assert result == input_regions

    def test_handles_none_input(self):
        """Test that None input returns None."""
        assert expand_wales_region(None) is None

    def test_handles_empty_list(self):
        """Test that empty list is passed through."""
        assert expand_wales_region([]) == []

    def test_expands_multiple_wales_instances(self):
        """Test that multiple 'Wales' entries are handled correctly."""
        result = expand_wales_region(["Wales", "Wales", "London English Region"])
        # Should only add Welsh regions once
        assert len(result) == 6
        assert result.count("London English Region") == 1


class TestCollapseWelshRegions:
    def test_collapses_all_welsh_regions_to_wales(self):
        """Test that all 5 Welsh regions are collapsed to 'Wales'."""
        input_regions = list(WELSH_REGIONS)
        result = collapse_welsh_regions(input_regions)
        assert len(result) == 1
        assert result == ["Wales"]

    def test_collapses_partial_welsh_regions(self):
        """Test that even partial Welsh regions are collapsed to 'Wales'."""
        input_regions = ["South Wales East PER", "North Wales PER"]
        result = collapse_welsh_regions(input_regions)
        assert len(result) == 1
        assert result == ["Wales"]

    def test_collapses_welsh_with_english_regions(self):
        """Test that Welsh regions are collapsed while keeping English regions."""
        input_regions = list(WELSH_REGIONS) + [
            "London English Region",
            "North East English Region",
        ]
        result = collapse_welsh_regions(input_regions)
        assert len(result) == 3
        assert "Wales" in result
        assert "London English Region" in result
        assert "North East English Region" in result
        # Ensure all Welsh regions are removed
        assert all(region not in result for region in WELSH_REGIONS)

    def test_returns_sorted_list(self):
        """Test that the result is sorted alphabetically."""
        input_regions = [
            "South Wales East PER",
            "London English Region",
            "North East English Region",
        ]
        result = collapse_welsh_regions(input_regions)
        assert result == sorted(result)
        assert result == ["London English Region", "North East English Region", "Wales"]

    def test_passes_through_non_welsh_regions(self):
        """Test that lists without Welsh regions are passed through."""
        input_regions = ["London English Region", "North East English Region"]
        result = collapse_welsh_regions(input_regions)
        assert result == input_regions

    def test_handles_empty_list(self):
        """Test that empty list is passed through."""
        assert collapse_welsh_regions([]) == []

    def test_handles_none_input(self):
        """Test that None input returns None."""
        assert collapse_welsh_regions(None) is None
