# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from datetime import datetime
from io import StringIO

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError


def export_to_s3(
    logger,
    df,
    skip_s3_upload,
    aws_region_name,
    s3_bucket_name,
    s3_filename,
    endpoint_url=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    expected_bucket_owner=None,
):
    """Export final mart to s3."""

    if skip_s3_upload == "TRUE":
        try:
            logger.info("Skipping S3 upload: SKIP_S3_UPLOAD=true")
        except Exception:
            pass
        return df

    # connect to s3
    logger.info("Connecting to S3")
    try:
        if endpoint_url and aws_access_key_id and aws_secret_access_key:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url=endpoint_url,
            )
        else:

            s3_client = boto3.client(
                "s3",
                region_name=aws_region_name,
            )
        logger.info("Successfully connected to S3")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Error with AWS credentials: {str(e)}")
        return None

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # upload file
    logger.info("Uploading file to S3: bucket=%s key=%s", s3_bucket_name, s3_filename)
    try:
        put_kwargs = {
            "Bucket": s3_bucket_name,
            "Key": s3_filename,
            "Body": csv_buffer.getvalue(),
        }
        if expected_bucket_owner:
            put_kwargs["ExpectedBucketOwner"] = expected_bucket_owner

        response = s3_client.put_object(
            **put_kwargs,
        )
        # Log the successful upload
        logger.info(
            f"Successfully uploaded `{s3_filename}` to S3 bucket `{s3_bucket_name}`. ✨"
        )
        return response
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {e}")
        return None
