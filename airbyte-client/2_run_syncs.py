import os
from dotenv import load_dotenv
from core import auth, connections

def main():
    """
    Scenario 2: Run all connectors.
    Fetches Connection ID from .env and triggers the sync.
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


    # 2. Load Connection ID
    epc_connection_id = os.getenv("EPC_CONNECTION_ID")
    if not epc_connection_id:
        print("Error: EPC_CONNECTION_ID not found in environment variables.")
        return

    # 3. Trigger Sync
    print(f"Triggering sync for connection: {epc_connection_id}")
    epc_job_id = connections.trigger_sync(
        client=client,
        connection_id=epc_connection_id
    )
    print(f"Sync triggered. Job ID: {epc_job_id}")
    
    # 4. Check Sync Status
    epc_job_status = connections.check_sync(
        client=client,
        job_id=epc_job_id
    )
    print(f"Job Status: {epc_job_status}")
    
if __name__ == "__main__":
    main()
