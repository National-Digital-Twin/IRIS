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
    
    # 2. Create Workspace
    workspace_id = workspaces.create_workspace(
        client=client,
        workspace_name=os.getenv("WORKSPACE_NAME")
    )
    print(f"Workspace ID: {workspace_id}")

    # 3. Create EPC Source
    print("Creating sources...")
    source_id = sources.create_s3_source(
        client=client,
        workspace_id=workspace_id,
        source_name=os.getenv("EPC_SOURCE_NAME"),
        streams_params=[json.loads(os.getenv("EPC_CERTIFICATES_STREAM_PARAMS"))],
        bucket=os.getenv("S3_BUCKET_NAME"),
        auth_mode=os.getenv("S3_AUTH_MODE"),
        access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
        secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        role_arn=os.getenv("S3_IAM_ROLE_ARN"),
        endpoint=os.getenv("S3_ENDPOINT")
    )
    print(f"Source ID: {source_id}")

    # 4. Create Destination
    destination_id = destinations.create_postgres_destination(
        client=client,
        workspace_id=workspace_id,
        destination_name=os.getenv("DESTINATION_NAME"),
        database=os.getenv("DATABASE_NAME"),
        host=os.getenv("DATABASE_HOST"),
        port=int(os.getenv("DATABASE_PORT")),
        username=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        schema=os.getenv("DATABASE_SCHEMA")
    )
    print(f"Destination ID: {destination_id}")

    # 5. Create Connection
    epc_connection_id = connections.create_connection(
        client=client,
        source_id=source_id,
        destination_id=destination_id,
        name=os.getenv("EPC_CONNECTION_NAME")
    )
    print(f"Connection ID: {epc_connection_id}")

    print("\nIMPORTANT: Copy these IDs to your .env file now!")

if __name__ == "__main__":
    main()
