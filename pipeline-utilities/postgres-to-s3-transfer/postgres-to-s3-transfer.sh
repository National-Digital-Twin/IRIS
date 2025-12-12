#!/usr/bin/env bash
set -euo pipefail

# Required inputs (can be set via --env-file or explicit -e flags)
: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_SCHEMA:?DB_SCHEMA is required}"
: "${S3_BUCKET:?S3_BUCKET is required}"

# File to export and output path
FILE="${FILE:-/tmp/${TABLE}.csv}"

echo "Exporting ${TABLE} to ${FILE} ..."
psql "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}" \
  -c "\copy (select * from ${DB_SCHEMA}.${TABLE}) to '${FILE}' with (format csv, header, force_quote *)"

AWS_ARGS=()

# Optional: pass in S3 endpoint for local use
if [[ -n "${S3_ENDPOINT:-}" ]]; then
  AWS_ARGS+=(--endpoint-url "$S3_ENDPOINT")
fi

echo "Uploading to s3://${S3_BUCKET}/${S3_DIR}/${TABLE}.csv"
aws "${AWS_ARGS[@]}" s3 cp "${FILE}" "s3://${S3_BUCKET}/${S3_DIR}/${TABLE}.csv"

rm -f "${FILE}"
echo "Cleaned up local file ${FILE}"
