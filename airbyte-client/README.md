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
- Airbyte authentication: `AUTHENTICATION_REQUIRED` ("TRUE" or "FALSE")
- Airbyte auth (if authentication enabled): `AIRBYTE_SERVER_URL`, `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`.
- Workspace/IDs: `WORKSPACE_NAME`, `WORKSPACE_ID`, `SOURCE_ID`, `DESTINATION_ID`, `EPC_CONNECTION_ID`.
- Connection naming: `EPC_SOURCE_NAME`, `EPC_CONNECTION_NAME`, `DESTINATION_NAME`.
- Source config: `EPC_CERTIFICATES_STREAM_PARAMS` (JSON string with `stream_name`, `globs`), `S3_BUCKET_NAME`, `S3_AUTH_MODE` (set to "role" or "access_key"), `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_IAM_ROLE_ARN`, `S3_ENDPOINT`.
- Destination config: `DATABASE_NAME`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_SCHEMA`.

## Scripts
- `1_create_resources.py`: create workspace, S3 source, Postgres destination, connection; prints IDs—copy them into `.env`.
- `2_run_syncs.py`: trigger and check a sync for `EPC_CONNECTION_ID`.
- `3_update_resources.py`: patch source/destination/connection using current `.env` values (e.g., renamed stream).
- `4_delete_resources.py`: delete the workspace and associated connectors (uses `WORKSPACE_ID`).

## Tips
- Run from inside `airbyte-client` so `.env` is picked up by `load_dotenv()`.
- If stream/schema changes, run script 3 after updating `EPC_CERTIFICATES_STREAM_PARAMS` to refresh the connection catalog.
