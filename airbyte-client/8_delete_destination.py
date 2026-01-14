import os, json
from dotenv import load_dotenv
from core import auth, destinations

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
    
    # Delete destination
    destinations.delete_destination(
        client=client,
        destination_id=os.getenv("DESTINATION_ID")
    )
    
    print(f"""Destination ID DELETED: {os.getenv("DESTINATION_ID")}""")


if __name__ == "__main__":
    main()