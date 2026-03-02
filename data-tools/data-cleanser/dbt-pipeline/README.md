Welcome to the dbt pipelines for IRIS data cleansing.

### Pre-requisites
- Python version >= 3.11 and < 3.12
- Install dependencies with `pip install -r requirements.txt`
- Create `.env` from `.env.local` and set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_SCHEMA`, `DB_PORT`
- For S3 export, set `S3_BUCKET_NAME`, `S3_FILENAME`, `AWS_REGION`, and optionally `EXPECTED_BUCKET_OWNER` to enforce bucket ownership checks
- Ensure source tables exist for the staging models you run

### Projects
- `dbt-epc` – core EPC transforms
- `dbt-epc-no-uprn` – EPC records lacking UPRN (to be refactored to use OS Places API)
- `dbt-os-ngd-address` – OS NGD Address transforms
- `dbt-os-ngd-buildings` – OS NGD Buildings transforms

### Run locally
From `dbt-pipeline`, ensure you have exported the variables from your .env one way or another.

Then, run:
`dbt deps --project-dir <dbt-directory>` which installs the necessary dbt dependencies.

Then run `dbt run --project-dir <dbt-directory> --profiles-dir <dbt-directory>` to run the dbt pipeline.

Then run `dbt test --project-dir <dbt-directory> --profiles-dir <dbt-directory>` to run dbt tests and validation checks against the data produced in the dbt run step.

### Container builds
Each project has its own Dockerfile in its directory. Build from the `dbt-pipeline` root:
```sh
docker build -f dbt-epc/Dockerfile -t dbt-epc .
docker build -f dbt-epc-no-uprn/Dockerfile -t dbt-epc-no-uprn .
docker build -f dbt-os-ngd-address/Dockerfile -t dbt-os-ngd-address .
docker build -f dbt-os-ngd-buildings/Dockerfile -t dbt-os-ngd-buildings .
```
Before running, ensure that all required environment variables are defined. Use .env.local as a guide. Once ready, run with your environment (or `--env-file ../.env` if you store it at repo root) e.g.:
```sh
docker run --rm --env-file ../.env dbt-epc
```

### Resources
- dbt docs: https://docs.getdbt.com/docs/introduction
- Discourse: https://discourse.getdbt.com
- Slack: https://community.getdbt.com/
- Events: https://events.getdbt.com
- Blog: https://blog.getdbt.com
