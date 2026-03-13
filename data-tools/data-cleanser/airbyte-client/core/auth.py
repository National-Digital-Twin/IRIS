import airbyte_api
from airbyte_api import models
import requests

def get_authenticated_client(server_url, auth_required=False, client_id=None, client_secret=None):
    """
    Authenticates with the Airbyte API using credentials from environment variables.
    
    Args:
        server_url (str): The URL for the airbyte server
        auth_required (bool): True/False whether authentication is enabled in the Airbyte instance.
        client_id (str): The ID of the client (required only if auth_required==True).
        client_secret (str): The secret of the client (required only if auth_required==True).

    Returns:
        airbyte_api.AirbyteAPI: An authenticated Airbyte client.
    """
    
    if auth_required:
    
        # Get the Bearer Token from Airbyte
        token_response = requests.post(
            f"{server_url}/applications/token",
            json={
                "client_id": client_id,
                "client_secret": client_secret
            }
        )

        if token_response.status_code == 200:
            token = token_response.json()["access_token"]
            print("Successfully authenticated.")
        else:
            print(f"Authentication failed: {token_response.status_code} - {token_response.text}")

        
        # Initialize and return the AirbyteAPI client
        client = airbyte_api.AirbyteAPI(
            server_url=server_url,
            security=models.Security(
                    bearer_auth=token
                    )
            )
        return client
    
    else: 
        return airbyte_api.AirbyteAPI(server_url=server_url)
