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
    object_key_prefix,
    s3_filename_user,
):
    """Export final mart to s3."""

    if skip_s3_upload:
        logger.info("-" * 100, "SKIPPING S3 UPLOAD", "-" * 100)
        return df

    # connect to s3
    logger.info("CONNECTING TO S3")
    try:
        s3_client = boto3.client(
            "s3",
            region_name=aws_region_name,
        )
        logger.info("Successfully connected to s3")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Error with AWS credentials: {str(e)}")
        return None

    bucket_name = s3_bucket_name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    user_string = f"{user}_" if (user := s3_filename_user) else ""
    object_key = f"{object_key_prefix}_{user_string}{timestamp}.csv"

    # check bucket exists
    logger.info("CHECKING S3 BUCKET EXISTS")
    try:
        # Check if the bucket exists and is accessible
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info("Successfully connected to bucket")
    except ClientError as e:
        logger.error(f"Error: Could not access the S3 bucket: {e}")
        return None

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # upload file
    logger.info("UPLOADING FILE")
    try:
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=csv_buffer.getvalue(),
        )
        # Log the successful upload
        logger.info(
            f"Successfully uploaded `{object_key}` to S3 bucket `{bucket_name}`. ✨"
        )
        return response
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {e}")
        return None
