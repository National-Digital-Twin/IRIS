import os
import json
from dotenv import load_dotenv
from core import auth, sources, destinations, connections

def main():
    """
    Scenario 3: Update sources and destinations.
    Refetches .env variables and patches existing resources.
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

    # 2. Update Source
    source_id = sources.update_s3_source(
        client=client,
        workspace_id=os.getenv("WORKSPACE_ID"),
        source_id=os.getenv("SOURCE_ID"),
        source_name=os.getenv("SOURCE_NAME"),
        streams_params=[json.loads(os.getenv("STREAMS_PARAMS"))],
        bucket=os.getenv("S3_BUCKET_NAME"),
        auth_mode=os.getenv("S3_AUTH_MODE"),
        access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
        secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        role_arn=os.getenv("S3_IAM_ROLE_ARN"),
        endpoint=os.getenv("S3_ENDPOINT")
    )
    print(f"Updated source ID: {source_id}")
    


    # 3. Update Destination
    destination_id = destinations.update_postgres_destination(
        client=client,
        workspace_id=os.getenv("WORKSPACE_ID"),
        destination_id=os.getenv("DESTINATION_ID"),
        destination_name=os.getenv("DESTINATION_NAME"),
        database=os.getenv("DATABASE_NAME"),
        host=os.getenv("DATABASE_HOST"),
        port=int(os.getenv("DATABASE_PORT")),
        username=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        schema=os.getenv("DATABASE_SCHEMA")
    )
    print(f"Updated destination ID: {destination_id}")
    
    # 4. Update Connection
    connection_id = connections.update_connection(
        client=client,
        connection_id=os.getenv("CONNECTION_ID"),
        streams_params=[json.loads(os.getenv("STREAMS_PARAMS"))]
    )
    print(f"Updated connection ID: {connection_id}")
    
    print("Resources updated successfully.")

if __name__ == "__main__":
    main()
