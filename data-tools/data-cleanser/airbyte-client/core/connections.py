from airbyte_api import models, api

def create_connection(client, source_id, destination_id, name):
    """
    Creates a connection between a source and a destination.

    Args:
        client: The authenticated Airbyte client.
        source_id (str): The ID of the source.
        destination_id (str): The ID of the destination.
        name (str): The name of the connection.

    Returns:
        str: The ID of the created connection.
    """
    # Create the connection
    create_connection_response = client.connections.create_connection(
        request=models.ConnectionCreateRequest(
            destination_id=destination_id,
            source_id=source_id,
            name=name,
        )
    )

    return create_connection_response.connection_response.connection_id


def trigger_sync(client, connection_id):
    """
    Triggers a sync job for a connection.

    Args:
        client: The authenticated Airbyte client.
        connection_id (str): The ID of the connection.

    Returns:
        str: The ID of the started job.
    """
    # Run the connector
    job_response = client.jobs.create_job(
        request=models.JobCreateRequest(
            connection_id=connection_id,
            job_type=models.JobTypeEnum.SYNC
        )
    )
    return job_response.job_response.job_id

def check_sync(client, job_id):
    """
    Checks the status of a sync job.

    Args:
        client: The authenticated Airbyte client.
        job_id (str): The ID of the job.

    Returns:
        str: The status of the job.
    """
    # Get the job status
    job_response = client.jobs.get_job(
        request=api.GetJobRequest(
            job_id=job_id
        )
    )
    return job_response.job_response.status

def update_connection(client, connection_id, streams_params):
    """Updates a connection catalog with provided stream definitions.

    Note: Airbyte expects ConnectionPatchRequest.configurations to be
    StreamConfigurationsInput containing StreamConfiguration entries
    (connection-level catalog), not source stream configs.
    """

    # Fetch current connection to preserve sync modes, cursor fields, etc.
    current = client.connections.get_connection(
        request=api.GetConnectionRequest(connection_id=connection_id)
    ).connection_response

    # Build new StreamConfiguration list, swapping in new stream names from params.
    # Assumes one-to-one mapping by order. Adjust mapping logic if multiple streams.
    new_streams = []
    for params, existing in zip(streams_params, current.configurations.streams):
        selected_fields = existing.selected_fields if existing.selected_fields else None
        new_streams.append(
            models.StreamConfiguration(
                name=params["stream_name"],
                sync_mode=existing.sync_mode,
                cursor_field=existing.cursor_field,
                primary_key=existing.primary_key,
                namespace=existing.namespace,
                destination_object_name=existing.destination_object_name,
                include_files=existing.include_files,
                mappers=existing.mappers,
                selected_fields=selected_fields,
            )
        )

    update_connection_response = client.connections.patch_connection(
        request=api.PatchConnectionRequest(
            connection_patch_request=models.ConnectionPatchRequest(
                configurations=models.StreamConfigurationsInput(streams=new_streams)
            ),
            connection_id=connection_id,
        )
    )

    return update_connection_response.connection_response.connection_id
    
def delete_connection(client, connection_id):
    """
    Deletes a connection.
    """
    
    # Delete the connection
    client.connections.delete_connection(
        request=api.DeleteConnectionRequest(
            connection_id=connection_id
        )
    )
    
