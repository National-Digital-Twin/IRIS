# INSTALLATION

**Repository:** `IRIS-data-cleanser`

**Description:** `Details how to install and run the pipeline`

**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0 `

## Prerequisites
Before using this repository, ensure you have the following dependencies installed:
- **Required Tooling:** Python, Poetry, Postgres, Airbyte, dbt, Docker

### 1. Download
```sh
git clone https://github.com/IRIS-data-cleanser.git
cd IRIS-data-cleanser
```

### 2. Install Dependencies

It is recommended to use a Python virtual environment (venv) to manage versions of the dependencies. This repository uses `poetry` to manage its dependencies. The baselined version of the dependencies can be found within the `poetry.lock` file. Run the following command within your virtual environment to install the dependencies: `poetry install --no-root --sync`.

Airbyte and Postgres instances can be installed using Docker. For Postgres, you can use the following command:
```
docker run --name postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 -d postgres
```

For Airbyte, follow the steps on their quickstart page [here](https://docs.airbyte.com/using-airbyte/getting-started/oss-quickstart).

### 3. Configuration

Following installation of Airbyte, add the connection details for Postgres in as a destination and import the `.yaml` files within the `airbyte/` directory.

Once the data is loaded into Postgres, you can run the following command within the `data_cleansing_pipeline` directory to build the models.
```
dbt run
```
To run a specific model, you can run:
```
dbt run --select <model_name>
```
To successfully run all dbt models, ensure that you have appropriate AWS access keys (with write access to S3) configured in your environment as well as a `S3_BUCKET_NAME` environment variable where you would like to persist your outputs from the pipeline.

## Deployment

Within the `airbyte/source-epc-recommendations` directory, there is an EPC Recommendations source connector, written in Python. This can be run in Airbyte as a Docker image.

### Locally running the connector docker image

#### Build

Run this command within the `airbyte/source-epc-recommendations` directory.

```
docker build . -t airbyte/source-epc-recommendations:dev
```

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-epc-recommendations:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-epc-recommendations:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-epc-recommendations:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-epc-recommendations:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json

© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
Licensed under the Open Government Licence v3.0.
For full licensing terms, see [OGL_LICENSE.md](OGL_LICENSE.md).