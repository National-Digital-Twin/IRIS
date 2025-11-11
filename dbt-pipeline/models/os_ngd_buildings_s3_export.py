# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Example Usage:

dbt run -s os_ngd_buildings_s3_export
"""

import os

import typer
from dotenv import load_dotenv
from export import export_to_s3
from logging_config import setup_logger


def model(dbt, fal):
    """Interoperate with dbt fal's dbt run command."""

    # load credentials from .env
    load_dotenv(".env", verbose=True)

    SKIP_S3_UPLOAD = os.environ.get("SKIP_S3_UPLOAD", False)
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    S3_FILENAME_USER = os.environ.get("S3_FILENAME_USER")
    AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")
    DEBUG = os.environ.get("DEBUG", True)

    logger = setup_logger(DEBUG)

    logger.info("Starting S3 export model")
    df = dbt.ref("int_os_ngd_buildings")
    try:
        logger.info("OS NGD Buildings columns: %s", list(df.columns))
        logger.info("OS NGD Buildings shape: %s", getattr(df, "shape", None))
    except Exception:
        pass

    logger.info(
        "S3 config SKIP=%s BUCKET=%s USER=%s REGION=%s",
        SKIP_S3_UPLOAD,
        S3_BUCKET_NAME,
        S3_FILENAME_USER,
        AWS_REGION_NAME,
    )

    export_to_s3(
        logger,
        df,
        SKIP_S3_UPLOAD,
        "eu-west-2",
        "iris-data-cleasnser-output",
        "os_ngd_buildings_s3_export",
        "dsm",
    )
    return df
