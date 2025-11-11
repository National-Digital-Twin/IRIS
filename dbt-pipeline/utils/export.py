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

    if skip_s3_upload == "TRUE":
        try:
            logger.info("Skipping S3 upload: SKIP_S3_UPLOAD=true")
        except Exception:
            pass
        return df

    # connect to s3
    logger.info("Connecting to S3")
    try:
        s3_client = boto3.client(
            "s3",
            region_name=aws_region_name,
        )
        logger.info("Successfully connected to S3")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Error with AWS credentials: {str(e)}")
        return None

    bucket_name = s3_bucket_name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    user_string = f"{user}_" if (user := s3_filename_user) else ""
    object_key = f"{object_key_prefix}_{user_string}{timestamp}.csv"

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # upload file
    logger.info("Uploading file to S3: bucket=%s key=%s", bucket_name, object_key)
    try:
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=csv_buffer.getvalue(),
        )
        # Log the successful upload
        logger.info(f"Successfully uploaded `{object_key}` to S3 bucket `{bucket_name}`. ✨")
        return response
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {e}")
        return None
