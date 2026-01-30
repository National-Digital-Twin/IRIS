# INSTALLATION

**Repository:** `iris-api`\
**Description:** `This document contains detailed installation steps, including required dependencies and setup configurations.`\
**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0`

## Prerequisites

Please ensure you have the following installed before building and running the API.
  - Python version 3.12.0
  - make
  - Apache Jena Fuseki

Once Apache Jena Fuseki is installed please follow the steps below:
  - Create two datasets in Fuseki one named knowledge and the other ontology.
  - Load the ontology ttl files in this repo into the ontology dataset (again, use the Fuseki UI) - this will provide the API with access to the ontologies.
  - Add your test data (e.g. buildings.ttl) to the knowledge dataset.

## Create PAT token

Create a personal access token (classic) on GitHub. Once this has been created please set it as an environment variable using the following command.

```sh
export GITHUB_ACCESS_TOKEN=<your-pat-token>
```

## Install dependencies

Please ensure the dependencies are installed using the command below:

```sh
pip install -r requirements.txt
```

## Running the server

To run the API please execute the command below:

```sh
make run-api
```
## Unit Tests

Unit tests can be run by running the following command in the root directory: `python -m pytest`

An Insomnia (https://insomnia.rest/) test suite is also provided as a JSON config file - `ndt-write-insomnia.json`

