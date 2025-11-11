#!/usr/bin/env python3
"""
Generate ~5 km bounding boxes for OS NGD regions without requiring OSGB projection data.

Workflow:
1. Read a region polygon from GeoJSON (expected in EPSG:4326 / CRS84).
2. Convert the polygon to Web Mercator (EPSG:3857) using closed-form equations.
3. Create a grid of square tiles (default 5 000 m) covering the polygon.
4. Keep tiles whose centroids fall inside the polygon.
5. Output the tile bboxes either in EPSG:4326 (default) or EPSG:3857.

This keeps area calculations in metres while still letting the Airbyte connector send
bounding boxes in a CRS accepted by the OS NGD Buildings API.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

try:
    from shapely.geometry import MultiPolygon as ShapelyMultiPolygon  # type: ignore
    from shapely.geometry import Polygon as ShapelyPolygon  # type: ignore
    from shapely.geometry import box as shapely_box  # type: ignore
    from shapely.prepared import prep as shapely_prep  # type: ignore
except Exception:  # pragma: no cover
    ShapelyPolygon = None  # type: ignore
    ShapelyMultiPolygon = None  # type: ignore
    shapely_box = None  # type: ignore
    shapely_prep = None  # type: ignore

EARTH_RADIUS_M = 6378137.0  # Web Mercator sphere radius
WEB_MERCATOR_MAX_LAT = 85.0511287798066

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTDIR = SCRIPT_DIR / "out"


def _slug(value: str) -> str:
    return value.strip().replace("/", "-").replace(" ", "_").replace("__", "_").replace("__", "_")


def normalize_output_crs(value: Optional[str]) -> str:
    if not value:
        return "EPSG:4326"
    v = value.strip().upper()
    if v in {"EPSG:4326", "4326", "CRS84", "HTTP://WWW.OPENGIS.NET/DEF/CRS/OGC/1.3/CRS84"}:
        return "EPSG:4326"
    if v in {"EPSG:3857", "3857"}:
        return "EPSG:3857"
    raise ValueError("output CRS must be EPSG:4326 or EPSG:3857")


@dataclass
class Tile:
    minx: float
    miny: float
    maxx: float
    maxy: float


def lonlat_to_webmerc(lon: float, lat: float) -> Tuple[float, float]:
    lat = max(min(lat, WEB_MERCATOR_MAX_LAT), -WEB_MERCATOR_MAX_LAT)
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    x = EARTH_RADIUS_M * lon_rad
    y = EARTH_RADIUS_M * math.log(math.tan(math.pi / 4 + lat_rad / 2))
    return (x, y)


def webmerc_to_lonlat(x: float, y: float) -> Tuple[float, float]:
    lon = math.degrees(x / EARTH_RADIUS_M)
    lat = math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS_M)) - math.pi / 2)
    return (lon, lat)


def parse_bbox_arg(bbox: str) -> Tuple[float, float, float, float]:
    parts = [p.strip() for p in bbox.split(",")]
    if len(parts) != 4:
        raise ValueError("--bbox must be 'min_lon,min_lat,max_lon,max_lat'")
    return tuple(map(float, parts))  # type: ignore


def load_region_geometry_4326(
    region_geojson_path: str, region_name: str
) -> List[List[List[Tuple[float, float]]]]:
    with open(region_geojson_path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    name_keys = ["RGN24NM", "RGN22NM", "RGN21NM", "name", "NAME"]

    for feat in gj.get("features", []):
        props = feat.get("properties", {}) or {}
        for key in name_keys:
            if props.get(key) == region_name:
                geom = feat.get("geometry", {})
                coords = geom.get("coordinates", [])
                if geom.get("type") == "Polygon":
                    multipoly = [coords]
                elif geom.get("type") == "MultiPolygon":
                    multipoly = coords
                else:
                    raise ValueError(f"Unsupported geometry type: {geom.get('type')}")
                result: List[List[List[Tuple[float, float]]]] = []
                for poly in multipoly:
                    rings: List[List[Tuple[float, float]]] = []
                    for ring in poly:
                        rings.append([(float(lon), float(lat)) for lon, lat in ring])
                    result.append(rings)
                return result

    raise ValueError(f"Region '{region_name}' not found in {region_geojson_path}")


def multipolygon_to_webmerc(
    mp_4326: List[List[List[Tuple[float, float]]]]
) -> List[List[List[Tuple[float, float]]]]:
    transformed: List[List[List[Tuple[float, float]]]] = []
    for poly in mp_4326:
        new_poly: List[List[Tuple[float, float]]] = []
        for ring in poly:
            new_poly.append([lonlat_to_webmerc(lon, lat) for lon, lat in ring])
        transformed.append(new_poly)
    return transformed


def multipolygon_bounds(
    mp: Sequence[Sequence[Sequence[Tuple[float, float]]]]
) -> Tuple[float, float, float, float]:
    minx = math.inf
    miny = math.inf
    maxx = -math.inf
    maxy = -math.inf
    for poly in mp:
        for ring in poly:
            for x, y in ring:
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x)
                maxy = max(maxy, y)
    if any(math.isinf(v) for v in (minx, miny, maxx, maxy)):
        raise RuntimeError("Region geometry is empty; cannot compute bounds")
    return (minx, miny, maxx, maxy)


def lonlat_bbox_to_webmerc(
    bbox_lonlat: Tuple[float, float, float, float]
) -> Tuple[float, float, float, float]:
    min_lon, min_lat, max_lon, max_lat = bbox_lonlat
    minx, miny = lonlat_to_webmerc(min_lon, min_lat)
    maxx, maxy = lonlat_to_webmerc(max_lon, max_lat)
    return (min(minx, maxx), min(miny, maxy), max(minx, maxx), max(miny, maxy))


def snap_floor(value: float, step: int) -> float:
    return math.floor(value / step) * step


def snap_ceil(value: float, step: int) -> float:
    return math.ceil(value / step) * step


def grid_tiles_from_bbox(
    bbox: Tuple[float, float, float, float], tile_size_m: int
) -> Iterable[Tile]:
    minx, miny, maxx, maxy = bbox
    x0 = snap_floor(minx, tile_size_m)
    y0 = snap_floor(miny, tile_size_m)
    x1 = snap_ceil(maxx, tile_size_m)
    y1 = snap_ceil(maxy, tile_size_m)

    y = y0
    while y < y1:
        x = x0
        while x < x1:
            yield Tile(x, y, x + tile_size_m, y + tile_size_m)
            x += tile_size_m
        y += tile_size_m


def point_in_ring(point: Tuple[float, float], ring: List[Tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    n = len(ring)
    if n < 3:
        return False
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-16) + x1):
            inside = not inside
    return inside


def point_in_multipolygon(
    point: Tuple[float, float], mp: List[List[List[Tuple[float, float]]]]
) -> bool:
    for poly in mp:
        if not poly:
            continue
        outer = poly[0]
        holes = poly[1:]
        if point_in_ring(point, outer):
            if not any(point_in_ring(point, hole) for hole in holes):
                return True
    return False


def build_shapely_polygon(
    polygons_merc: Optional[List[List[List[Tuple[float, float]]]]]
):
    if not polygons_merc or ShapelyPolygon is None:
        return None
    shapely_polys = []
    for poly in polygons_merc:
        if not poly:
            continue
        shell = poly[0]
        if len(shell) < 3:
            continue
        holes = [ring for ring in poly[1:] if len(ring) >= 3]
        try:
            shapely_polys.append(ShapelyPolygon(shell, holes if holes else None))
        except Exception:
            continue
    if not shapely_polys:
        return None
    if len(shapely_polys) == 1:
        return shapely_polys[0]
    if ShapelyMultiPolygon is None:
        return shapely_polys[0]
    return ShapelyMultiPolygon(shapely_polys)


def maybe_filter_tiles_by_region(
    tiles: Iterable[Tile],
    region_polygons: Optional[List[List[List[Tuple[float, float]]]]],
    region_geom=None,
) -> List[Tile]:
    if not region_polygons:
        return list(tiles)

    if region_geom is not None and shapely_box is not None and shapely_prep is not None:
        prepared = shapely_prep(region_geom)
        filtered = []
        for tile in tiles:
            rect = shapely_box(tile.minx, tile.miny, tile.maxx, tile.maxy)
            if prepared.intersects(rect):
                filtered.append(tile)
        return filtered

    # Fallback: without shapely we skip geometry-based filtering so that the full
    # bounding box is covered (guaranteeing no gaps even if it means extra tiles).
    return list(tiles)


def format_coord(value: float) -> str:
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def tile_bounds(tile: Tile, output_crs: str) -> Tuple[float, float, float, float]:
    if output_crs == "EPSG:3857":
        return (tile.minx, tile.miny, tile.maxx, tile.maxy)
    lon_min, lat_min = webmerc_to_lonlat(tile.minx, tile.miny)
    lon_max, lat_max = webmerc_to_lonlat(tile.maxx, tile.maxy)
    return (lon_min, lat_min, lon_max, lat_max)


def tile_to_text(tile: Tile, region_code: str, output_crs: str) -> str:
    minx, miny, maxx, maxy = tile_bounds(tile, output_crs)
    parts = [format_coord(v) for v in (minx, miny, maxx, maxy)]
    return f"{','.join(parts)}|{region_code}"


def write_text_lines(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            if line.strip():
                f.write(line + "\n")


def export_tiles_geojson(path: Path, tiles: List[Tile], output_crs: str) -> None:
    features = []
    for tile in tiles:
        minx, miny, maxx, maxy = tile_bounds(tile, output_crs)
        ring = [
            [minx, miny],
            [maxx, miny],
            [maxx, maxy],
            [minx, maxy],
            [minx, miny],
        ]
        features.append(
            {
                "type": "Feature",
                "properties": {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy},
                "geometry": {"type": "Polygon", "coordinates": [ring]},
            }
        )
    fc = {"type": "FeatureCollection", "features": features, "crs": output_crs}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(fc, f)


def export_preview_html(path: Path, tiles: List[Tile], region_geojson_path: Optional[str]) -> None:
    try:
        import folium  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("folium is required for HTML preview") from exc

    if not tiles:
        return
    cx = (tiles[0].minx + tiles[0].maxx) / 2
    cy = (tiles[0].miny + tiles[0].maxy) / 2
    lon0, lat0 = webmerc_to_lonlat(cx, cy)
    m = folium.Map(location=[lat0, lon0], zoom_start=7, tiles="OpenStreetMap")

    if region_geojson_path:
        try:
            with open(region_geojson_path, "r", encoding="utf-8") as f:
                gj = json.load(f)

            def _style(_):
                return {"fill": False, "color": "#999999", "weight": 1, "opacity": 0.7}

            folium.GeoJson(gj, name="Regions", style_function=_style).add_to(m)
        except Exception as err:
            print(f"[warn] Could not overlay region boundaries on HTML: {err}")

    for tile in tiles:
        ring = [
            webmerc_to_lonlat(tile.minx, tile.miny)[::-1],  # lat, lon
            webmerc_to_lonlat(tile.maxx, tile.miny)[::-1],
            webmerc_to_lonlat(tile.maxx, tile.maxy)[::-1],
            webmerc_to_lonlat(tile.minx, tile.maxy)[::-1],
            webmerc_to_lonlat(tile.minx, tile.miny)[::-1],
        ]
        folium.PolyLine(ring, color="#3388ff", weight=1, opacity=0.8).add_to(m)

    path.parent.mkdir(parents=True, exist_ok=True)
    m.save(path)


def export_preview_png(
    path: Path,
    tiles: List[Tile],
    region_polygons_merc: Optional[List[List[List[Tuple[float, float]]]]],
) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
        from matplotlib.collections import PatchCollection  # type: ignore
        from matplotlib.patches import Rectangle  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("matplotlib is required for PNG preview") from exc

    fig, ax = plt.subplots(figsize=(8, 8))

    if region_polygons_merc:
        for poly in region_polygons_merc:
            for ring in poly:
                xs = [pt[0] for pt in ring]
                ys = [pt[1] for pt in ring]
                ax.plot(xs, ys, color="#aaaaaa", linewidth=0.5, alpha=0.7)

    patches = [
        Rectangle((tile.minx, tile.miny), tile.maxx - tile.minx, tile.maxy - tile.miny)
        for tile in tiles
    ]
    if patches:
        pc = PatchCollection(patches, facecolor="none", edgecolor="#3388ff", linewidths=0.3)
        ax.add_collection(pc)

    if tiles:
        minx = min(tile.minx for tile in tiles)
        miny = min(tile.miny for tile in tiles)
        maxx = max(tile.maxx for tile in tiles)
        maxy = max(tile.maxy for tile in tiles)
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

    ax.set_aspect("equal")
    ax.set_title("Tiles (Web Mercator metres)")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate ~5 km tiles for OS NGD regions (no external PROJ data needed)"
    )
    parser.add_argument("--region-geojson", help="GeoJSON with regions (EPSG:4326 / CRS84)")
    parser.add_argument("--region-name", help="Region name (e.g. 'South East')")
    parser.add_argument("--region-code", required=True, help="Region code (e.g. E12000008)")
    parser.add_argument(
        "--bbox",
        help="Fallback bbox in lon/lat as 'min_lon,min_lat,max_lon,max_lat' (used if no region polygon)",
    )
    parser.add_argument("--tile-size-m", type=int, default=5000, help="Tile size in metres")
    parser.add_argument(
        "--output-crs",
        default="EPSG:4326",
        help="CRS for emitted bbox strings (EPSG:4326 or EPSG:3857). Default EPSG:4326.",
    )
    parser.add_argument("--outdir", default=None, help="Output directory (default: ./out next to script)")
    parser.add_argument("--no-joined", action="store_true", help="Skip *_joined.txt outputs")
    parser.add_argument("--no-geojson", action="store_true", help="Skip GeoJSON export")
    parser.add_argument("--no-preview-html", action="store_true", help="Skip HTML preview")
    parser.add_argument("--no-preview-png", action="store_true", help="Skip PNG preview")

    args = parser.parse_args()

    if not args.bbox and not (args.region_geojson and args.region_name):
        parser.error("Either --bbox or (--region-geojson and --region-name) must be provided.")

    output_crs = normalize_output_crs(args.output_crs)
    outdir = Path(args.outdir).expanduser() if args.outdir else DEFAULT_OUTDIR

    region_mp_4326 = None
    region_mp_merc = None
    bbox_merc: Optional[Tuple[float, float, float, float]] = None

    if args.region_geojson and args.region_name:
        region_mp_4326 = load_region_geometry_4326(args.region_geojson, args.region_name)
        region_mp_merc = multipolygon_to_webmerc(region_mp_4326)
        bbox_merc = multipolygon_bounds(region_mp_merc)

    if args.bbox:
        bbox_lonlat = parse_bbox_arg(args.bbox)
        bbox_merc = lonlat_bbox_to_webmerc(bbox_lonlat)

    if bbox_merc is None:
        raise RuntimeError("Unable to determine a bounding box for tile generation.")

    region_shapely = build_shapely_polygon(region_mp_merc)

    tiles = list(grid_tiles_from_bbox(bbox_merc, args.tile_size_m))
    tiles = maybe_filter_tiles_by_region(tiles, region_mp_merc, region_shapely)

    region_slug = _slug(args.region_name or args.region_code)
    base_a = outdir / f"tiles_{region_slug}"
    base_b = outdir / f"tiles_{args.region_code}"

    text_lines = [tile_to_text(tile, args.region_code, output_crs) for tile in tiles]

    write_text_lines(base_a.with_suffix(".txt"), text_lines)
    if base_b != base_a:
        write_text_lines(base_b.with_suffix(".txt"), text_lines)

    if not args.no_joined:
        joined = "|||".join(line for line in text_lines if line)
        base_a.parent.mkdir(parents=True, exist_ok=True)
        (base_a.parent / f"{base_a.name}_joined.txt").write_text(joined, encoding="utf-8")
        if base_b != base_a:
            (base_b.parent / f"{base_b.name}_joined.txt").write_text(joined, encoding="utf-8")

    if not args.no_geojson:
        export_tiles_geojson(base_a.with_suffix(".geojson"), tiles, output_crs)

    if not args.no_preview_html:
        try:
            export_preview_html(base_a.parent / f"{base_a.name}_preview.html", tiles, args.region_geojson)
        except Exception as err:
            print(f"[warn] Could not write HTML preview: {err}")

    if not args.no_preview_png:
        try:
            export_preview_png(
                base_a.parent / f"{base_a.name}_preview.png",
                tiles,
                region_mp_merc,
            )
        except Exception as err:
            print(f"[warn] Could not write PNG preview: {err}")

    wrote = [str(base_a.with_suffix(".txt"))]
    if base_b != base_a:
        wrote.append(str(base_b.with_suffix(".txt")))
    if not args.no_joined:
        wrote.append(str(base_a.parent / f"{base_a.name}_joined.txt"))
        if base_b != base_a:
            wrote.append(str(base_b.parent / f"{base_b.name}_joined.txt"))
    print("Wrote: " + ", ".join(wrote))


if __name__ == "__main__":
    main()
