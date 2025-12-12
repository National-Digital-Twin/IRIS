# postgres-to-s3-transfer utility

Exports a Postgres table to CSV and uploads it to S3/MinIO using psql and awscli.

## Inputs (env vars)
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SCHEMA (required)
- TABLE (required)
- S3_BUCKET (required)
- S3_DIRECTORY (required)
- S3_ENDPOINT (optional; set for MinIO or custom endpoints)
- AWS creds (optional; rely on IAM/IRSA if not set)

## Build and run (from this directory)
`docker build -t postgres-to-s3-transfer -f Dockerfile .`

`docker run --rm --env-file .env postgres-to-s3-transfer`

Or set envs explicitly:
docker run --rm \
  -e DB_HOST=... -e DB_PORT=... -e DB_USER=... -e DB_PASSWORD=... -e DB_NAME=... -e DB_SCHEMA=...\
  -e TABLE=mart_address_profiling \
  -e S3_BUCKET=raw-data -e S3_DIR=epc/ -e S3_ENDPOINT=http://minio:9000 \
  epc-export
