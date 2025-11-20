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


WELSH_REGIONS = {
    "South Wales East PER",
    "North Wales PER",
    "Mid and West Wales PER",
    "South Wales West PER",
    "South Wales Central PER",
}


def is_welsh_region(region_name: str) -> bool:
    return region_name in WELSH_REGIONS


def expand_wales_region(area_names: list[str] | None) -> list[str] | None:
    """
    Expand 'Wales' to individual Welsh regions for database queries.

    If the list contains 'Wales', it is replaced with all individual Welsh regions.
    Other region names are passed through unchanged.

    Args:
        area_names: List of area names, potentially including 'Wales'

    Returns:
        list[str] | None: List with 'Wales' expanded to individual regions, or None if input is None

    Examples:
        >>> expand_wales_region(['Wales'])
        ['South Wales East PER', 'North Wales PER', ...]
        >>> expand_wales_region(['Wales', 'London'])
        ['London', 'South Wales East PER', 'North Wales PER', ...]
        >>> expand_wales_region(['London'])
        ['London']
    """
    if area_names is None or "Wales" not in area_names:
        return area_names

    return [name for name in area_names if name != "Wales"] + sorted(WELSH_REGIONS)


def collapse_welsh_regions(regions: list[str]) -> list[str]:
    """
    Collapse individual Welsh regions to 'Wales' in a region list.

    If all or any Welsh regions are present in the list, they are replaced with 'Wales'.
    Other region names are passed through unchanged.

    Args:
        regions: List of region names, potentially including Welsh regions

    Returns:
        list[str]: List with Welsh regions collapsed to 'Wales', sorted alphabetically

    Examples:
        >>> collapse_welsh_regions_in_list(['South Wales East PER', 'North Wales PER', 'London'])
        ['London', 'Wales']
        >>> collapse_welsh_regions_in_list(['London', 'North East'])
        ['London', 'North East']
    """
    if not regions:
        return regions

    non_welsh = [r for r in regions if r not in WELSH_REGIONS]
    if len(non_welsh) == len(regions):
        return regions

    return non_welsh + ["Wales"]
