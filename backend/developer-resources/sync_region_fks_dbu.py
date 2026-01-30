import os

import psycopg2

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "iris")
DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

UNSYNCED_CHECK_SCRIPT = """
    SELECT COUNT(*) FROM iris.district_borough_unitary
    WHERE english_region_fid IS NULL AND scotland_and_wales_region_fid IS NULL;
"""

SYNCED_CHECK_SCRIPT = """
    SELECT COUNT(*) FROM iris.district_borough_unitary
    WHERE english_region_fid IS NOT NULL AND scotland_and_wales_region_fid IS NULL
    OR english_region_fid IS NULL AND scotland_and_wales_region_fid IS NOT NULL;
"""

ENGLISH_REGION_UPDATE_SCRIPT = """
     CREATE TEMP TABLE temp_english_region(
        fid INT,
        geometry geometry(MultiPolygon, 4326)
    );

    INSERT INTO temp_english_region
        SELECT fid, ST_TRANSFORM(ST_BUFFER(ST_TRANSFORM(geometry, 27700), 5000::double precision), 4326) as geometry
        FROM iris.english_region;

    UPDATE iris.district_borough_unitary dbu
    SET english_region_fid = r.fid
    FROM (
        SELECT fid, geometry
        FROM temp_english_region
    ) r
    WHERE ST_CONTAINS(r.geometry, ST_SIMPLIFY(dbu.geometry, 0.0001::double precision));
"""

SCOTLAND_AND_WALES_REGION_UPDATE_SCRIPT = """
    CREATE TEMP TABLE temp_scotland_and_wales_region(
        fid INT,
        geometry geometry(MultiPolygon, 4326)
    );

    INSERT INTO temp_scotland_and_wales_region
        SELECT fid, ST_TRANSFORM(ST_BUFFER(ST_TRANSFORM(geometry, 27700), 5000::double precision), 4326) as geometry
        FROM iris.scotland_and_wales_region;

    UPDATE iris.district_borough_unitary dbu
    SET scotland_and_wales_region_fid = r.fid
    FROM (
        SELECT fid, geometry
        FROM temp_scotland_and_wales_region
    ) r
    WHERE ST_CONTAINS(r.geometry, ST_SIMPLIFY(dbu.geometry, 0.0001::double precision));
"""


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


if __name__ == "__main__":
    print("Syncing region foriegn keys on district_borough_unitary table...")
    unsynced_records = run_db_command(UNSYNCED_CHECK_SCRIPT, fetchone=True)

    print(f"{unsynced_records} records to sync.")

    if unsynced_records > 0:
        run_db_command(ENGLISH_REGION_UPDATE_SCRIPT)
        run_db_command(SCOTLAND_AND_WALES_REGION_UPDATE_SCRIPT)

        synced_records = run_db_command(SYNCED_CHECK_SCRIPT, fetchone=True)

        print(f"Synced region foriegn keys for {synced_records} records.")
    else:
        print("No records to sync.")
