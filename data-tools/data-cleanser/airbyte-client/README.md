Airbyte Python client helpers for creating, updating, running, and deleting Airbyte resources from scripts.

## Prereqs
- Python 3.11+
- Access to your Airbyte instance (OAuth client ID/secret) 
- Access to minio (local) via access key ID or s3 (deployed) via IAM role
- Access to Postgres (local) via local credentials or RDS (deployed) via deployed credentials

## Docker containers (for local usage)
- Ensure docker is installed on your machine.
- Start airbyte if not already running using [official documentation](https://docs.airbyte.com/platform/using-airbyte/getting-started/oss-quickstart#install-abctl-the-fast-way-mac-linux). There's no need to download Docker Desktop if you don't want to. 
  - For ease of use, install with authentication **disabled** using [this guidance](https://docs.airbyte.com/platform/deploying-airbyte/integrations/authentication#turning-off-authentication).
- Run `docker compose up -d` from within the airbyte-client directory. 

## Environment setup
- Recommended (uv):  
  - `cd airbyte-client`  
  - `uv venv && uv sync` (uses `pyproject.toml` / `uv.lock`)  
  - Run commands with `uv run python <script>`.
- Alternative (pip):  
  - `python -m venv .venv && source .venv/bin/activate`  
  - `pip install -r requirements.txt`.
- `.venv/` is ignored; only commit `pyproject.toml`, `uv.lock`, and (optionally) `requirements.txt`.

## MINIO config (local)
- Log into MINIO UI, create and configure bucket and directories and load data. 

## Configure env vars
Create `airbyte-client/.env` (copy from `.env.example` if present) with:
- Airbyte authentication mode: `AUTHENTICATION_REQUIRED` ("TRUE" or "FALSE")
- Airbyte server URL: `AIRBYTE_SERVER_URL` (typically `http://<url>/api/public/v1`)
- Airbyte auth (if authentication enabled): `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`.
- Workspace config: `WORKSPACE_NAME`, `WORKSPACE_ID`
- S3 Source config: `STREAMS_PARAMS` (JSON string with `stream_name`, `globs`), `S3_BUCKET_NAME`, `S3_AUTH_MODE` (set to "role" or "access_key"), `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_IAM_ROLE_ARN`, `S3_ENDPOINT`, `SOURCE_ID` (if source created)
- Destination config: `DATABASE_NAME`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_SCHEMA`, `DESTINATION_ID` (if destination created)
- Connection config: `CONNECTION_NAME`, `CONNECTION_ID` (if connection created)

## Scripts
- `1_create_workspace.py`: create workspace
- `2_create_s3_source.py`: create S3 source
- `3_create_postgres_destination.py`: create Postgres destination
- `4_create_connection.py`: create connection
- `5_update_resources.py`: update source, destination and connection using latest environment variables.
- `6_delete_all_resources.py`: delete workspace, sources and destinations
- `7_delete_source`: delete source using source ID in .env
- `8_delete_destination.py`: delete destination using destination ID in .env
- `9_delete_connection.py`: delete connection using connection ID in .env
- `10_run_syncs.py`: trigger and check a sync for connection using connection ID in .env

## Tips
- Run from inside `airbyte-client` so `.env` is picked up by `load_dotenv()`.
- If stream/schema changes, run script 5 after updating `STREAMS_PARAMS` to refresh the connection catalog.
