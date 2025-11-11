Tile generation (5 km) for OS NGD Buildings
===========================================

CLI examples

- South East:
  `python make_tiles.py --region-geojson Regions_December_2024_Boundaries_EN_BGC_-3699623982958172124.geojson --region-name "South East" --region-code E12000008 --tile-size-m 5000 --outdir out/`

- South West:
  `python make_tiles.py --region-geojson airbyte/infra/spatial/Regions_December_2024_Boundaries_EN_BGC_-3699623982958172124.geojson --region-name "South West" --region-code E12000009 --tile-size-m 5000 --outdir out/`

- Fallback if you do not have a region polygon (manual bbox in EPSG:27700):
  `python make_tiles.py --bbox "526000,120000,615000,210000" --region-code E12000008 --tile-size-m 5000 --outdir out/`

Outputs

- `tiles_<region>.txt`: Plain TEXT, one line per tile: `minx,miny,maxx,maxy|REGION_CODE`
- Optional QC only (Airbyte does not read these):
  - `tiles_<region>.geojson` (EPSG:27700 grid polygons)
  - `tiles_<region>_preview.html` (Folium, EPSG:4326)
  - `tiles_<region>_preview.png` (matplotlib)

Feeding Airbyte (os_ngd_buildings.yaml)

- The Airbyte declarative source expects a single config string per region (e.g. `tiles_text_se`) where tiles are joined by `|||`.
- Default: `*_joined.txt` is written automatically next to the line-by-line files. Copy the contents of `*_joined.txt` into the matching `tiles_text_*` field in Airbyte.
- Opt-out: pass `--no-joined` if you do not want the `*_joined.txt` files.
- Alternative (manual join):
  - Linux/macOS: `paste -sd '|||' out/tiles_South_East.txt > out/tiles_South_East_joined.txt`
  - Or: `awk '{printf NR==1?"%s":"|||%s", $0}' out/tiles_South_East.txt > out/tiles_South_East_joined.txt`

Notes

- Region detection uses the `RGN24NM` property in the provided Regions GeoJSON.
- If Folium/Matplotlib/pyproj are unavailable in your environment, the tool will still write the TEXT file and skip previews.
