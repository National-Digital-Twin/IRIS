import os, json
from dotenv import load_dotenv
from core import auth, connections

def main():
    """
    Delete source.
    Reads config from .env, deletes resources, and prints IDs for manual saving.
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
    
    # Delete connection
    connections.delete_connection(
        client=client,
        connection_id=os.getenv("CONNECTION_ID")
    )
    
    print(f"""Connection ID DELETED: {os.getenv("CONNECTION_ID")}""")


if __name__ == "__main__":
    main()