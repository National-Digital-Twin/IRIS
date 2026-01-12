import os, json
from dotenv import load_dotenv
from core import auth, workspaces, sources, destinations, connections

def main():
    """
    Create Workspace and Connectors.
    Reads config from .env, creates resources, and prints IDs for manual saving.
    """
    # 1. Authenticate
    load_dotenv()

    auth_required = (os.getenv("AUTHENTICATION_REQUIRED", "FALSE").strip().lower()=="true")
    client = auth.get_authenticated_client(
        server_url=os.getenv("AIRBYTE_SERVER_URL"), 
        auth_required=auth_required,
        client_id=os.getenv("AIRBYTE_CLIENT_ID", None), 
        client_secret=os.getenv("AIRBYTE_CLIENT_SECRET", None)
    )
    print("Airbyte API client created successfully")

    # Create Connection
    connection_id = connections.create_connection(
        client=client,
        source_id=os.getenv("SOURCE_ID"),
        destination_id=os.getenv("DESTINATION_ID"),
        name=os.getenv("CONNECTION_NAME")
    )
    print(f"Connection ID: {connection_id}")

    print("\nIMPORTANT: Copy these IDs to your .env file now!")

if __name__ == "__main__":
    main()
