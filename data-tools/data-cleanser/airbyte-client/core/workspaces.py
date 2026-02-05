from airbyte_api import models, api


def create_workspace(client, workspace_name):
    """
    Create a workspace in Airbyte.

    Args:
        client: The authenticated Airbyte client.
        workspace_name (str): The name of the workspace.

    Returns:
        str: The ID of the created workspace.
    """

    create_workspace_response = client.workspaces.create_workspace(
        request=models.WorkspaceCreateRequest(
            name=workspace_name
        )
    )
    
    return create_workspace_response.workspace_response.workspace_id

def delete_workspace(client, workspace_id):
    """
    Deletes a workspace in Airbyte.
    """
    
    client.workspaces.delete_workspace(
        request=api.DeleteWorkspaceRequest(
            workspace_id=workspace_id)
    )