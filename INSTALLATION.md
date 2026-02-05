# INSTALLATION

**Repository:** `IRIS`  
**Description:** `Combined installation instructions for the IRIS frontend and backend services.`  
**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0`

## Overview

This monorepo contains:
- `frontend/` — IRIS visualisation client (Angular).
- `backend/` — IRIS API service (Python).
- `data-tools/data-cleanser/` — ETL pipeline using Airbyte + dbt to prepare data for IRIS.

## Prerequisites

Common:
- Git

Frontend:
- NVM
- Node.js (via `frontend/.nvmrc`)
- Angular CLI

Backend:
- Python 3.12.0
- make
- Apache Jena Fuseki

Data cleanser:
- Python
- Poetry
- Postgres
- Airbyte
- dbt
- Docker

Data pipeline:
- Python 3.12+
- Docker
- Kafka
- Zookeeper

## GitHub Packages PAT

Some dependencies are hosted on GitHub Packages. Create a classic PAT with `read:packages` and export it:

```sh
export GITHUB_ACCESS_TOKEN=<your-pat-token>
```

## Backend (API) setup

### 1. Configure Fuseki

Once Apache Jena Fuseki is installed:
- Create two datasets in Fuseki: `knowledge` and `ontology`.
- Load the ontology TTL files from this repo into the `ontology` dataset.
- Add test data (e.g., `buildings.ttl`) to the `knowledge` dataset.

### 2. Install dependencies

```sh
cd backend
pip install -r requirements.txt
```

### 3. Run the API

```sh
make run-api
```

### 4. Tests

From the repo root:

```sh
python -m pytest
```

An Insomnia test suite is provided as `backend/ndt-write-insomnia.json`.

## Frontend (visualisation) setup

### 1. Install dependencies

```sh
cd frontend
nvm install
nvm use
npm install
```

### 2. Build required images (local dev)

For local development, build the following images:
- `iris-api` (from `backend/`)
- `iris-transparent-proxy` (from `frontend/transparent-proxy/`)
- `iris-sag` (from `frontend/developer_resources/`)

If you need to access GitHub Container Registry:

```sh
echo <my-pat-token> | docker login ghcr.io -u <my-username> --password-stdin
```

### 3. Local configuration

Create local environment and configuration files:
- `frontend/src/environments/environment.local.ts`
- `frontend/configurations/local/config.json`

These should match the structure of existing environment/config files and can contain secrets.

Create `frontend/src/environments/keys.environment.ts` and add Mapbox and OS Data Hub keys:

```ts
export const apiKeys = {
  mapbox: {
    apiKey: "your mapbox api key",
  },
  os: {
    apiKey: "your os data hub api key",
  },
};
```

### 4. Run the frontend

```sh
npm run start
```

Other available configurations:

```sh
npm run start:dev
npm run start:qa
npm run start:prod
```

### 5. Build

```sh
npm run build
```

### 6. Linting

```sh
npm run lint
```

## Data cleanser (ETL) setup

### 1. Install dependencies

It is recommended to use a Python virtual environment. This repository uses `poetry` to manage dependencies. The baselined versions are in `data-tools/data-cleanser/poetry.lock`.

```sh
cd data-tools/data-cleanser
poetry install --no-root --sync
```

Airbyte and Postgres can be installed with Docker. For Postgres:

```sh
docker run --name postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 -d postgres
```

For Airbyte, follow the OSS quickstart instructions in the Airbyte docs.

### 2. Configuration

After installing Airbyte, open the Airbyte UI and add Postgres as a destination. Then import the source `.yaml` files from `data-tools/data-cleanser/airbyte/`, create the connections, and sync them.

Once data is loaded into Postgres, run dbt from `data-tools/data-cleanser/data_cleansing_pipeline`:

```sh
dbt run
```

To run a specific model:

```sh
dbt run --select <model_name>
```

To run all dbt models, ensure AWS keys with write access to S3 are configured and `S3_BUCKET_NAME` is set.

### 3. Deployment (Airbyte connector)

The EPC Recommendations source connector is in `data-tools/data-cleanser/airbyte/source-epc-recommendations` and can be run in Airbyte as a Docker image.

Build and run locally:

```sh
cd data-tools/data-cleanser/airbyte/source-epc-recommendations
docker build . -t airbyte/source-epc-recommendations:dev
docker run --rm airbyte/source-epc-recommendations:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-epc-recommendations:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-epc-recommendations:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-epc-recommendations:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Data pipeline setup

### 1. Install dependencies

It is recommended to use `pip` and a Python virtual environment. Component dependencies live in `requirements.txt` files within each pipeline component.

Kafka and Zookeeper can be started locally with Docker using the root Makefile:

```sh
cd data-tools/data-pipeline
make start-kafka-docker
```

### 2. Configuration

Copy each `.env-local` to `.env` and populate required environment variables. For a local Kafka instance started via the Makefile, use:

- `BOOTSTRAP_SERVERS`: `localhost:9092`
- `SASL_USERNAME`: `user1`
- `SASL_PASSWORD`: `root`

Input data for adapter components should be generated by the data cleanser pipeline.

### 3. Deployment

Run pipeline components as Kubernetes jobs. From a component directory:

```sh
kubectl apply -f job.yaml
```

For file-based jobs, rebuild the container images after updating input files.

## Licensing

See `LICENSE.md` for full licensing terms.

© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
