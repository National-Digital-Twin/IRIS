# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Example Usage:

python -m address_base_plus_s3_export --input_file mart_parity_address_profiling.csv
dbt run -s address_base_plus_s3_export
"""

import os
from datetime import datetime
from io import StringIO

import boto3
import typer


def export(df):
    """Export final mart to s3."""
    if os.environ.get("SKIP_S3_UPLOAD"):
        return df

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION_NAME"),
    )
    bucket_name = os.environ.get("S3_BUCKET_NAME")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    user_string = f"{user}_" if (user := os.environ.get("S3_FILENAME_USER")) else ""
    object_key = f"address_base_plus_{user_string}{timestamp}.csv"

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    response = s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=csv_buffer.getvalue(),
    )
    typer.echo(f"Successfully uploaded `{object_key}` to S3 bucket. ✨")
    return response


def model(dbt, fal):
    """Interoperate with dbt fal's dbt run command."""
    df = dbt.ref("mart_address_base_plus")
    export(df)
    return df


def main(input_file: str):
    """Interoperate with python cli call."""
    return export(input_file)


if __name__ == "__main__":
    typer.run(main)
