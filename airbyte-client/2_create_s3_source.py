import os, json
from dotenv import load_dotenv
from core import auth, workspaces, sources, destinations, connections

def main():
    """
    Create Workspace and Connectors.
    Reads config from .env, creates resources, and prints IDs for manual saving.
    """
    # Authenticate
    load_dotenv()

    auth_required = (os.getenv("AUTHENTICATION_REQUIRED", "FALSE").strip().lower()=="true")
    client = auth.get_authenticated_client(
        server_url=os.getenv("AIRBYTE_SERVER_URL"), 
        auth_required=auth_required,
        client_id=os.getenv("AIRBYTE_CLIENT_ID", None), 
        client_secret=os.getenv("AIRBYTE_CLIENT_SECRET", None)
    )
    print("Airbyte API client created successfully")

    # Create Source
    print("Creating sources...")
    source_id = sources.create_s3_source(
        client=client,
        workspace_id=os.getenv("WORKSPACE_ID"),
        source_name=os.getenv("SOURCE_NAME"),
        streams_params=[json.loads(os.getenv("STREAMS_PARAMS"))],
        bucket=os.getenv("S3_BUCKET_NAME"),
        auth_mode=os.getenv("S3_AUTH_MODE"),
        access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
        secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        role_arn=os.getenv("S3_IAM_ROLE_ARN"),
        endpoint=os.getenv("S3_ENDPOINT")
    )
    print(f"Source ID: {source_id}")

    print("\nIMPORTANT: Copy these IDs to your .env file now!")

if __name__ == "__main__":
    main()
