# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import psycopg2


GPKG_SOURCE = os.getenv("GPKG_SOURCE")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "iris")
DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
TARGET_SCHEMA = os.getenv("TARGET_SCHEMA", "iris")
TARGET_TABLE = os.getenv("TARGET_TABLE", "wind_driven_rain_projections")
MATERIALIZED_VIEW = os.getenv("MATERIALIZED_VIEW", "iris.wind_driven_rain_projections_geojson")


def download_file(url: str, dest: Path):
    """Download a file from URL to destination."""
    print(f"Downloading {url} → {dest}")
    with urllib.request.urlopen(url) as response, open(dest, "wb") as out_file:
        out_file.write(response.read())
    print("Download complete.")
    

def run_db_command(command: str):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(command)
    conn.close()    


def run_ogr2ogr(gpkg_path: Path):
    """Run ogr2ogr to import GPKG into PostGIS."""
    pg_conn_str = (
        f"PG:host={DB_HOST} port={DB_PORT} "
        f"dbname={DB_NAME} user={DB_USERNAME} password={DB_PASSWORD}"
    )
    run_db_command(f"TRUNCATE {TARGET_SCHEMA}.{TARGET_TABLE};")
    cmd = [
        "ogr2ogr",
        "-f", "PostgreSQL",
        pg_conn_str,
        str(gpkg_path),
        "-nln", f"{TARGET_SCHEMA}.{TARGET_TABLE}",
        "-lco", "SCHEMA=" + TARGET_SCHEMA,
        "-append",
        "-t_srs", "EPSG:4326"
    ]
    # Redact password in the connection string for logging
    redacted_cmd = " ".join(cmd.copy())
    if "password=" in redacted_cmd:
        import re
        redacted_cmd = re.sub(r'password=[^ ]+', 'password=****', redacted_cmd)
    print("Running:", redacted_cmd)
    subprocess.run(cmd, check=True)
    print("ogr2ogr import complete.")


def refresh_materialized_view():
    print(f"Refreshing materialized view {MATERIALIZED_VIEW}")
    run_db_command(f"REFRESH MATERIALIZED VIEW {MATERIALIZED_VIEW};")
    print("Materialized view refresh complete.")


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        gpkg_file = Path(tmpdir) / "data.gpkg"
        download_file(GPKG_SOURCE, gpkg_file)
        run_ogr2ogr(gpkg_file)
        refresh_materialized_view()


if __name__ == "__main__":
    main()