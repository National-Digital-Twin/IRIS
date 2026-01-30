# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import csv
import io
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import boto3
import sqlalchemy as sa
from smart_open import open as smart_open
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

BATCH_SIZE = 50000


def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_int(int_str):
    if not int_str or not int_str.strip():
        return None
    try:
        return int(float(int_str.strip()))
    except ValueError:
        return None


def list_s3_csv_files(path):
    """List CSV files from S3 bucket."""
    path_parts = path[5:].split("/", 1)
    bucket = path_parts[0]
    prefix = path_parts[1] if len(path_parts) > 1 else ""

    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    csv_files = []

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if "Contents" not in page:
            continue
        for obj in page["Contents"]:
            if obj["Key"].lower().endswith(".csv"):
                csv_files.append(f"s3://{bucket}/{obj['Key']}")

    logger.info(f"Found {len(csv_files)} CSV files in {path}")
    return csv_files


def list_local_csv_files(path):
    """List CSV files from local filesystem."""
    p = Path(path)
    if not p.exists():
        logger.error(f"Path does not exist: {path}")
        return []

    csv_files = []
    if p.is_file() and p.suffix.lower() == ".csv":
        csv_files.append(str(p))
    elif p.is_dir():
        csv_files = [str(f) for f in p.glob("**/*.csv")]

    logger.info(f"Found {len(csv_files)} CSV files in {path}")
    return csv_files


def list_csv_files(path):
    """List CSV files from S3 bucket or local filesystem."""
    if path.startswith("s3://"):
        return list_s3_csv_files(path)
    else:
        return list_local_csv_files(path)


def process_batch(engine, batch):
    """Process a batch of EPC data."""
    if not batch:
        return 0

    with engine.begin() as conn:
        raw_conn = conn.connection

        conn.execute(
            text(
                """
            CREATE TEMP TABLE epc_temp (
                uprn TEXT,
                lodgement_date DATE,
                sap_rating INTEGER
            ) ON COMMIT DROP;
        """
            )
        )

        buffer = io.StringIO()
        for row in batch:
            buffer.write(
                f"{row['uprn']}\t{row['lodgement_date']}\t{row['sap_rating']}\n"
            )
        buffer.seek(0)

        raw_conn.cursor().copy_from(
            buffer,
            "epc_temp",
            columns=["uprn", "lodgement_date", "sap_rating"],
        )

        conn.execute(
            text(
                """
            UPDATE iris.epc_assessment ea
            SET sap_rating = et.sap_rating
            FROM epc_temp et
            WHERE ea.uprn = et.uprn AND ea.lodgement_date = et.lodgement_date;
            """
            )
        )


def process_csv_file(csv_path, engine):
    logger.info(f"Processing {csv_path}")

    batch = []
    file_rows = 0
    file_stats = {"processed": 0, "skipped": 0}

    with smart_open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")

        for row in reader:
            file_rows += 1

            certificate_type = row.get("CertificateType", "").strip()

            if certificate_type != "domestic":
                file_stats["skipped"] += 1
                continue

            sap_band = row.get("SAPBand", "").strip()
            if not sap_band:
                file_stats["skipped"] += 1
                continue

            uprn = row.get("UPRN", "").strip()
            lodgement_date = parse_date(row.get("LodgementDate", ""))
            sap_rating = parse_int(row.get("SAPRating", ""))
            if not uprn or not lodgement_date or sap_rating is None:
                file_stats["skipped"] += 1
                continue

            batch.append(
                {
                    "uprn": uprn,
                    "lodgement_date": lodgement_date,
                    "sap_rating": sap_rating,
                }
            )

            if len(batch) >= BATCH_SIZE:
                process_batch(engine, batch)
                file_stats["processed"] += len(batch)
                logger.info(
                    f"  Batch: {file_stats['processed']:,} processed, {file_stats['skipped']:,} skipped"
                )
                batch = []

    if batch:
        process_batch(engine, batch)
        file_stats["processed"] += len(batch)

    logger.info(
        f"Completed: {file_rows:,} scanned, "
        f"{file_stats['processed']:,} processed, "
        f"{file_stats['skipped']:,} skipped"
    )

    return file_stats


def main():
    # CSV_PATH can be:
    # - s3://bucket/prefix (S3 bucket)
    # - /path/to/folder (local directory)
    # - /path/to/file.csv (single local file)
    csv_path = os.getenv("CSV_PATH")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USERNAME", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "iris")

    if not all([csv_path, db_host, db_user, db_password]):
        logger.error(
            "Missing one or more required environment variables: CSV_PATH, DB_HOST, DB_USERNAME, DB_PASSWORD"
        )
        sys.exit(1)

    engine = sa.create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    csv_files = list_csv_files(csv_path)
    if not csv_files:
        logger.warning("No CSV files found")
        return

    stats = {"processed": 0, "skipped": 0}
    start_time = datetime.now()
    logger.info(f"Starting import of {len(csv_files)} file(s)")

    for csv_file in csv_files:
        file_start = datetime.now()
        try:
            file_stats = process_csv_file(csv_file, engine)
            stats["processed"] += file_stats["processed"]
            stats["skipped"] += file_stats["skipped"]

            file_elapsed = (datetime.now() - file_start).total_seconds()
            total_elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"File took {file_elapsed:.2f}s | Total time so far: {total_elapsed:.2f}s"
            )
        except Exception as e:
            logger.error(f"Failed to process {csv_file}: {e}")
            continue

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 60)
    logger.info("IMPORT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Rows processed:  {stats['processed']:,}")
    logger.info(f"Rows skipped:    {stats['skipped']:,}")
    logger.info(f"Total time:      {elapsed:.2f} seconds")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
