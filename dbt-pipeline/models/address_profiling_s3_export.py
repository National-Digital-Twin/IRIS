# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Example Usage:

python -m address_profiling_s3_export --input_file mart_parity_address_profiling_with_sap.csv
dbt run -s address_profiling_s3_export
"""

import os

import typer
from dotenv import load_dotenv
from utils.export import export_to_s3
from utils.logging_config import setup_logger

# load credentials from .env
load_dotenv(".env", verbose=True)

SKIP_S3_UPLOAD = os.environ.get("SKIP_S3_UPLOAD")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_FILENAME_USER = os.environ.get("S3_FILENAME_USER")
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")
DEBUG = os.environ.get("DEBUG", True)

print(SKIP_S3_UPLOAD, S3_BUCKET_NAME, S3_FILENAME_USER, AWS_REGION_NAME)  # noqa: T201

logger = setup_logger(DEBUG)


def model(dbt, fal):
    """Interoperate with dbt fal's dbt run command."""
    logger.info("-" * 100, "s3 export model", "-" * 100)
    df = dbt.ref("mart_address_profiling_with_sap")
    logger.info("-" * 100, "Address profiling data", "-" * 100)
    logger.info(df.columns)
    logger.info(df.shape)
    export_to_s3(
        logger,
        df,
        SKIP_S3_UPLOAD,
        AWS_REGION_NAME,
        S3_BUCKET_NAME,
        "address_profiling",
        S3_FILENAME_USER,
    )
    return df


def main(input_file: str):
    """Interoperate with python cli call."""
    return export_to_s3(
        logger,
        input,
        SKIP_S3_UPLOAD,
        AWS_REGION_NAME,
        S3_BUCKET_NAME,
        "address_profiling",
        S3_FILENAME_USER,
    )


if __name__ == "__main__":
    typer.run(main)
