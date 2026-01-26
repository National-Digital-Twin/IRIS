# EPC Address Matcher

Minimal utility to match EPC certificate addresses to UPRNs using OS Places and write a cross-reference table in Postgres.

## Prerequisites
This utility requires you to have a `certificates` table in a postgres database containing EPC certificates. 

### What it does
- Reads certificates without a UPRN from `certificates`.
- Calls OS Places to find the top UPRN candidate above a match threshold.
- Appends results to `epc_address_uprn_crossref` (by `lmk_key`), including unmatched rows with null `uprn`/`match_score` to avoid reprocessing.

### Environment
Required:
- `OS_PLACES_API_KEY`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_SCHEMA`, `DB_USER`, `DB_PASSWORD`

Optional:
- `MATCH_THRESHOLD` (0.8 by default)
- `LOG_LEVEL` ("INFO" by default)
- `LOG_INTERVAL` (1000 by default)
- `SLEEP_DURATION` (0.1 by default)
- `COMMIT_INTERVAL` (100 by default)
- `TIMEOUT_WAIT_TIME` (60 by default)
- `BACKOFF_WAIT_TIME` (15 by default)
- `MAX_RETRIES` (3 by default)

## Run locally

Create and activate a virtual environment using the included requirements.txt file.
Then run:

```bash
python match_uprn_os_places.py
```

## Run with Docker
```bash
docker build -t epc-address-matcher:latest .
docker run --rm --env-file .env epc-address-matcher:latest
```

## Output
- Table: `epc_address_uprn_crossref`
- Columns: `lmk_key`, `query_address`, `uprn`, `match_score`
