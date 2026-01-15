from airbyte_api import api, models


def build_s3_config(
    bucket,
    streams,
    endpoint,
    auth_mode,
    access_key_id=None,
    secret_access_key=None,
    role_arn=None,
    region_name=None,
):
    """Create configuration for s3 source.

    Args:
        bucket (str): The S3 bucket name.
        streams (list): List of streams for the source.
        endpoint (str): The S3 bucket endpoint.
        auth_mode (str): Set "role" to use IAM role. Set "access_key" to use access key id and secret access key.
        access_key_id (str, optional): Access key ID. Defaults to None.
        secret_access_key (str, optional): Secret access key. Defaults to None.
        role_arn (str, optional): IAM role. Defaults to None.
        region_name (str, optional): Region name. Defaults to None.

    Returns:
        models.SourceS3: s3 bucket configuration class
    """

    mode = (auth_mode or "").lower()
    if mode not in {"role", "access_key"}:
        raise ValueError(
            f"Invalid S3 auth_mode: {auth_mode}. Use 'role' or 'access_key'."
        )

    base = {"bucket": bucket, "streams": streams, "endpoint": endpoint}

    if mode == "role":
        if region_name is None:
            raise ValueError(
                f"If role mode is choosen then region_name should be provided"
            )
        base.update(role_arn=role_arn, region_name=region_name)
    else:
        base.update(
            aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key
        )
    return models.SourceS3(**base)


def create_s3_source(
    client,
    workspace_id,
    source_name,
    streams_params: list,
    bucket,
    auth_mode,
    access_key_id,
    secret_access_key,
    role_arn,
    endpoint,
    region_name: str,
):
    """
    Creates an S3 source in Airbyte.

    Args:
        client: The authenticated Airbyte client.
        workspace_id (str): The ID of the workspace.
        source_name (str): The name of the source.
        streams_params (list): A list of dictionaries. Each dictionary contains params for each stream:
            - stream_name (str): The name of the stream.
            - globs (list): List of glob patterns for files.

        bucket (str): The S3 bucket name.
        auth_mode (str): Either "role" or "access_key" to determine s3 bucket authentication.
        access_key_id (str, optional): Access key ID. Defaults to None.
        secret_access_key (str, optional): Secret access key. Defaults to None.
        role_arn (str, optional): IAM role. Defaults to None.
        endpoint (str): The S3 endpoint URL.

    Returns:
        str: The ID of the created source.
    """

    # create streams
    streams = []
    for params in streams_params:
        streams.append(
            models.SourceS3FileBasedStreamConfig(
                format=models.SourceS3CSVFormat(),
                name=params["stream_name"],
                globs=params["globs"],
            )
        )
    print(streams)

    configuration = build_s3_config(
        bucket=bucket,
        streams=streams,
        endpoint=endpoint,
        auth_mode=auth_mode,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        role_arn=role_arn,
        region_name=region_name,
    )

    create_source_response = client.sources.create_source(
        request=models.SourceCreateRequest(
            configuration=configuration, name=source_name, workspace_id=workspace_id
        )
    )

    return create_source_response.source_response.source_id


def update_s3_source(
    client,
    workspace_id,
    source_id,
    source_name,
    streams_params: list,
    bucket,
    auth_mode,
    access_key_id,
    secret_access_key,
    role_arn,
    endpoint,
):
    """
    Updates an s3 source in Airbyte.

    Args:
        client: The authenticated Airbyte client.
        workspace_id (str): The ID of the workspace.
        source_id (str): The ID of the source.
        source_name (str): The name of the source.
        streams_params (list): A list of dictionaries. Each dictionary contains params for each stream:
            - stream_name (str): The name of the stream.
            - globs (list): List of glob patterns for files.

        bucket (str): The S3 bucket name.
        auth_mode (str): Either "role" or "access_key" to determine s3 bucket authentication.
        access_key_id (str, optional): Access key ID. Defaults to None.
        secret_access_key (str, optional): Secret access key. Defaults to None.
        role_arn (str, optional): IAM role. Defaults to None.
        endpoint (str): The S3 endpoint URL.

    Returns:
        str: The ID of the updated source.
    """

    # create streams
    streams = []
    for params in streams_params:
        streams.append(
            models.SourceS3FileBasedStreamConfig(
                format=models.SourceS3CSVFormat(),
                name=params["stream_name"],
                globs=params["globs"],
            )
        )

    # create configuration
    configuration = build_s3_config(
        bucket=bucket,
        streams=streams,
        endpoint=endpoint,
        auth_mode=auth_mode,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        role_arn=role_arn,
    )

    update_source_response = client.sources.patch_source(
        request=api.PatchSourceRequest(
            source_id=source_id,
            source_patch_request=models.SourcePatchRequest(
                configuration=configuration, name=source_name, workspace_id=workspace_id
            ),
        )
    )

    return update_source_response.source_response.source_id


def delete_source(client, source_id):
    """
    Deletes a source in Airbyte.
    """

    client.sources.delete_source(request=api.DeleteSourceRequest(source_id=source_id))
