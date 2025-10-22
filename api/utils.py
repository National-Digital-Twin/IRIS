# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

pass_through_headers = [
    "X-Auth-Request-Access-Token",
    "Authorization",
]


def get_headers(headers):
    forward_headers = {}
    for header in pass_through_headers:
        hv = headers.get(header)
        if hv is not None:
            forward_headers[header] = hv
    return forward_headers


def has_bindings(r):
    return bool(r and r.get("results") and r.get("results").get("bindings"))


def validate_geojson_polygon(geojson_str: str) -> str:
    """
    Validates that a string is valid GeoJSON Polygon or MultiPolygon compatible with ST_GeomFromGeoJSON.

    Raises:
        ValueError: If the GeoJSON is invalid or not a Polygon/MultiPolygon type

    Returns:
        str: The validated GeoJSON string
    """
    import json

    try:
        geojson = json.loads(geojson_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")

    if not isinstance(geojson, dict):
        raise ValueError("GeoJSON must be a JSON object")

    if "type" not in geojson:
        raise ValueError("GeoJSON must have a 'type' field")

    valid_types = {"Polygon", "MultiPolygon"}
    if geojson["type"] not in valid_types:
        raise ValueError(
            f"GeoJSON type must be 'Polygon' or 'MultiPolygon', got '{geojson['type']}'"
        )

    if "coordinates" not in geojson:
        raise ValueError("GeoJSON must have a 'coordinates' field")

    if not isinstance(geojson["coordinates"], list):
        raise ValueError("GeoJSON 'coordinates' must be an array")

    return geojson_str
