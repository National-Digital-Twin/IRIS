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

    # Create Destination
    destination_id = destinations.create_postgres_destination(
        client=client,
        workspace_id=os.getenv("WORKSPACE_ID"),
        destination_name=os.getenv("DESTINATION_NAME"),
        database=os.getenv("DATABASE_NAME"),
        host=os.getenv("DATABASE_HOST"),
        port=int(os.getenv("DATABASE_PORT")),
        username=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        schema=os.getenv("DATABASE_SCHEMA")
    )
    print(f"Destination ID: {destination_id}")

    print("\nIMPORTANT: Copy these IDs to your .env file now!")

if __name__ == "__main__":
    main()
