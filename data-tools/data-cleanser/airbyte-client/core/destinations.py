from airbyte_api import models, api

def create_postgres_destination(client, workspace_id, destination_name, database, host, port, username, password, schema):
    """
    Creates a Postgres destination in Airbyte.

    Args:
        client: The authenticated Airbyte client.
        workspace_id (str): The ID of the workspace.
        destination_name (str): The name of the destination.
        database_name (str): The Postgres database name
        host (str): The Postgres hostname.
        port (str): The Postgres endpoint.
        username (str): The Postgres username.
        password (str): The Postgres password.
        schema (str): The Postgres schema to use.

    Returns:
        str: The ID of the created destination.
    """
    # Construct the DestinationPostgres configuration
    configuration=models.DestinationPostgres(
        database=database,
        host=host,
        port=port,
        username=username,
        password=password,
        schema=schema
    )
    
    # Call client.destinations.create_destination
    create_destination_response = client.destinations.create_destination(
        request=models.DestinationCreateRequest(
            configuration=configuration,
            name=destination_name, 
            workspace_id=workspace_id
        )
    )
    
    # Return the destination_id
    return create_destination_response.destination_response.destination_id

def update_postgres_destination(client, workspace_id, destination_id, destination_name, database, host, port, username, password, schema):
    """
    Updates a postgres destination in Airbyte

    Args:  
        client: The authenticated Airbyte client.
        workspace_id (str): The ID of the workspace.
        destination_id (str): The ID of the existing destination
        name (str): The name of the destination.
        host (str): The Postgres hostname.
        password (str): The Postgres password.
        schema (str): The Postgres schema to use.

    Returns:
        str: The ID of the created destination.
    """

    # Construct the DestinationPostgres configuration
    configuration=models.DestinationPostgres(
        database=database,
        host=host,
        port=port,
        username=username,
        password=password,
        schema=schema
    )
    
    # Call client.destinations.create_destination
    update_destination_response = client.destinations.patch_destination(
        request=api.PatchDestinationRequest(
            destination_id=destination_id,
            destination_patch_request=models.DestinationPatchRequest(
                configuration=configuration,
                name=destination_name
        )
    ))

    return update_destination_response.destination_response.destination_id


def delete_destination(client, destination_id):
    """
    Deletes a destination in Airbyte.
    """

    # Delete the destination
    client.destinations.delete_destination(
        request=api.DeleteDestinationRequest(
            destination_id=destination_id
        )
    )
