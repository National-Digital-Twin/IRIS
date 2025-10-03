# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import psycopg2

GPKG_SOURCE = os.getenv("GPKG_SOURCE")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "iris")
DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
GPKG_TABLE = os.getenv("GPKG_TABLE")
TARGET_SCHEMA = os.getenv("TARGET_SCHEMA", "iris")
TARGET_TABLE = os.getenv("TARGET_TABLE")
MATERIALIZED_VIEW = os.getenv("MATERIALIZED_VIEW")
JOIN_VIEW = os.getenv("JOIN_VIEW")
DATA_VIEW = os.getenv("DATA_VIEW")
GPKG_EXTENSION = ".gpkg"


def download_file(url: str, dest: Path):
    """Download a file from URL to destination."""
    print(f"Downloading {url} → {dest}")
    if url.endswith(GPKG_EXTENSION):
        with urllib.request.urlopen(url) as response, open(dest, "wb") as out_file:
            out_file.write(response.read())
        print("Download complete.")
    else:
        zip_file = os.path.join(dest, "data.zip")
        unzip_file = os.path.join(dest, "data")
        urllib.request.urlretrieve(url, zip_file)
        print(f"Zip file downloaded: {zip_file}")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(unzip_file)
            print(f"Extracted to : {unzip_file}")
            for root, dirs, files in os.walk(unzip_file):
                for file in files:
                    if file.endswith(GPKG_EXTENSION):
                        file_gpkg = os.path.join(root, file)
                        print(f"GeoPackage available: {file_gpkg}")
                        shutil.copyfile(file_gpkg, f"{dest}/data{GPKG_EXTENSION}")
                        outfile = f"{dest}/data.gpkg"
                        print(f"Download complete: {outfile}")
                    else:
                        print(f"No GeoPAckage found {file}")


def run_db_command(command: str, fetchone=False):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(command)
        if fetchone:
            row = cur.fetchone()
            return row[0] if row else None
    conn.close()


def is_table_populated():
    count = run_db_command(
        f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{TARGET_TABLE};", fetchone=True
    )
    return count > 0


def run_ogr2ogr(gpkg_path: Path):
    """Run ogr2ogr to import GPKG into PostGIS."""
    pg_conn_str = (
        f"PG:host={DB_HOST} port={DB_PORT} "
        f"dbname={DB_NAME} user={DB_USERNAME} password={DB_PASSWORD}"
    )
    run_db_command(f"TRUNCATE {TARGET_SCHEMA}.{TARGET_TABLE};")
    cmd = [
        "ogr2ogr",
        "-f",
        "PostgreSQL",
        pg_conn_str,
        str(gpkg_path),
        "-nln",
        f"{TARGET_SCHEMA}.{TARGET_TABLE}",
        "-lco",
        "SCHEMA=" + TARGET_SCHEMA,
        "-append",
        "-t_srs",
        "EPSG:4326",
    ]
    # Redact password in the connection string for logging
    redacted_cmd = " ".join(cmd.copy())
    if "password=" in redacted_cmd:
        import re

        redacted_cmd = re.sub(r"password=[^ ]+", "password=****", redacted_cmd)
    print("Running:", redacted_cmd)
    subprocess.run(cmd, check=True)
    print("ogr2ogr import complete.")


def run_ogr2ogr_table(gpkg_path: Path):
    """Run ogr2ogr_table to import a single table GPKG into PostGIS."""
    pg_conn_str = (
        f"PG:host={DB_HOST} port={DB_PORT} "
        f"dbname={DB_NAME} user={DB_USERNAME} password={DB_PASSWORD}"
    )
    run_db_command(f"TRUNCATE {TARGET_SCHEMA}.{TARGET_TABLE} CASCADE;")
    cmd = [
        "ogr2ogr",
        "-f",
        "PostgreSQL",
        pg_conn_str,
        str(gpkg_path),
        "-nln",
        f"{TARGET_SCHEMA}.{TARGET_TABLE}",
        "-lco",
        "SCHEMA=" + TARGET_SCHEMA,
        "-sql",
        f"SELECT * FROM {GPKG_TABLE}",
        "-append",
        "-t_srs",
        "EPSG:4326",
    ]
    # Redact password in the connection string for logging
    redacted_cmd = " ".join(cmd.copy())
    if "password=" in redacted_cmd:
        import re

        redacted_cmd = re.sub(r"password=[^ ]+", "password=****", redacted_cmd)
    print("Running:", redacted_cmd)
    subprocess.run(cmd, check=True)
    print("ogr2ogr import complete.")


def refresh_materialized_view():
    if MATERIALIZED_VIEW is not None and MATERIALIZED_VIEW != "":
        print(f"Refreshing materialized view {MATERIALIZED_VIEW}")
        run_db_command(f"REFRESH MATERIALIZED VIEW {MATERIALIZED_VIEW};")
        print("Materialized view refresh complete.")
    else:
        print("No materialized view given to refresh.")


def refresh_join_view():
    if JOIN_VIEW is not None and JOIN_VIEW != "":
        print(f"Refreshing materialized view {JOIN_VIEW}")
        run_db_command(f"REFRESH MATERIALIZED VIEW {JOIN_VIEW};")
        print("Materialized view refresh complete.")
    else:
        print("No join view given to refresh.")


def refresh_data_view():
    if DATA_VIEW is not None and DATA_VIEW != "":
        print(f"Refreshing materialized view {DATA_VIEW}")
        run_db_command(f"REFRESH MATERIALIZED VIEW {DATA_VIEW};")
        print("Materialized view refresh complete.")
    else:
        print("No data view given to refresh.")


def handle_geopackage(tmpdir):
    gpkg_file = Path(tmpdir) / f"data{GPKG_EXTENSION}"
    download_file(GPKG_SOURCE, gpkg_file)
    if GPKG_TABLE == "none":
        run_ogr2ogr(gpkg_file)
    else:
        run_ogr2ogr_table(gpkg_file)


def handle_zip(tmpdir):
    zip_file = Path(tmpdir)
    gpkg_file = Path(tmpdir) / f"data{GPKG_EXTENSION}"
    download_file(GPKG_SOURCE, zip_file)
    if GPKG_TABLE == "none":
        run_ogr2ogr(gpkg_file)
    else:
        run_ogr2ogr_table(gpkg_file)
        refresh_join_view()
        refresh_data_view()


def main():
    if not is_table_populated():
        with tempfile.TemporaryDirectory() as tmpdir:
            if GPKG_SOURCE.endswith(GPKG_EXTENSION):
                handle_geopackage(tmpdir)
            else:
                handle_zip(tmpdir)
            refresh_materialized_view()
    else:
        print(
            f"Table {TARGET_SCHEMA}.{TARGET_TABLE} already populated. Skipping data load."
        )


if __name__ == "__main__":
    main()
