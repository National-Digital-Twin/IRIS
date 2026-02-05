# README

**Repository:** `IRIS`  
**Description:** `Monorepo containing the IRIS frontend and backend services.`  
**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0`  

## Overview

IRIS is a digital tool designed to support data-driven decision-making for retrofitting domestic properties by identifying homes that could benefit from energy efficiency improvements. It enables stakeholders to assess housing stock based on energy performance data to help target funding schemes and policy interventions more effectively. IRIS is part of the NDTP Demonstrator Programme.

This monorepo contains:
- `frontend/` — the IRIS visualisation client (Angular).
- `backend/` — the IRIS API service (Python).
- `data-tools/data-cleanser/` — ETL pipeline using Airbyte + dbt to prepare data for IRIS.
- `data-tools/data-pipeline/` — data pipelines to process EPC and geographic data.

## Repository Structure

```
.
├── frontend/  # IRIS visualisation client
├── backend/   # IRIS API service
├── data-tools/data-cleanser/ # ETL pipeline for IRIS data preparation
└── data-tools/data-pipeline/ # Data pipelines for EPC and geographic processing
```

## Prerequisites

Common:
- Git

Frontend:
- NVM (recommended)
- Node.js (via `.nvmrc`)
- Angular CLI

Backend:
- Python 3.12
- Docker
- make

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

## Quick Start

### 1. Clone
```sh
git clone https://github.com/National-Digital-Twin/IRIS.git
cd IRIS
```

### 2. Frontend (visualisation)

```sh
cd frontend
nvm install
nvm use
```

If you need access to GitHub Packages, create a classic token with `read:packages` and export it:
```sh
export GITHUB_ACCESS_TOKEN=ghp_xxxxxxx
```

```sh
npm install
ng build
```

System requirements (frontend):
- Dual-Core CPU (Intel i5 or AMD Ryzen 3 equivalent), 8GB RAM, SSD/HDD with 10GB free space

For more details, see `frontend/INSTALLATION.md` and `frontend/UNINSTALL.md`.

### 3. Backend (API)

```sh
cd backend
pip install -f requirements.txt
make run-api
```

System requirements (backend):
- Dual-Core CPU (Intel i5 or AMD Ryzen 3 equivalent), 8GB RAM, SSD/HDD with 10GB free space

For more details, see `backend/INSTALLATION.md` and `backend/UNINSTALL.md`.

### 4. Data cleanser (ETL)

```sh
cd data-tools/data-cleanser
poetry --version
```

For detailed install and run steps, see `data-tools/data-cleanser/INSTALLATION.MD` and `data-tools/data-cleanser/UNINSTALL.md`.

### 5. Data pipeline

```sh
cd data-tools/data-pipeline
python --version
```

For detailed install and run steps, see `data-tools/data-pipeline/INSTALLATION.md` and `data-tools/data-pipeline/UNINSTALL.md`.

## Data Cleanser (ETL)

The data cleanser is an ETL pipeline that fetches and transforms EPC and OS data for IRIS. It uses Airbyte for extraction and dbt for transformations, with outputs persisted to S3.

Key components:
- Airbyte sources and destinations in `data-tools/data-cleanser/airbyte/`
- dbt models in `data-tools/data-cleanser/dbt-pipeline/`

For full details, see `data-tools/data-cleanser/README.md`.

## Data Pipeline

The data pipeline contains two major pipelines:
- `address-profiling-pipeline` for EPC assessment data processing.
- `lat-long-pipeline` for geographic coordinate processing.

Both pipelines use adapters and mappers to ingest source data (CSV or S3) and publish to Kafka topics as RDF outputs.

For full details, see `data-tools/data-pipeline/README.md`.

## Features

Frontend:
- **Core functionality** Visualises housing data on a map, including materials and EPC ratings.
- **Scalability & performance** Code optimised for scalability and performance.

Backend:
- **Core functionality** Provides API routes to serve and route data to and from the visualisation client.
- **Key integrations** REST interface to query and write data to the IA node.
- **Scalability & performance** Optimised for scalability and performance.

Data cleanser:
- **Core functionality** ETL pipeline to ingest EPC/OS data and prepare datasets for IRIS.
- **Key integrations** Airbyte sources/destinations and dbt transformations with S3 outputs.

Data pipeline:
- **Core functionality** Address profiling and lat/long pipelines to transform EPC and geographic data into RDF.
- **Key integrations** Kafka topics for adapter/mapper components.

## API Documentation

The API documentation can be accessed by running the backend and navigating to:
- `/api-docs`
- `/api-docs/openapi.json`

## Public Funding Acknowledgment

This repository has been developed with public funding as part of the National Digital Twin Programme (NDTP), a UK Government initiative. NDTP, alongside its partners, has invested in this work to advance open, secure, and reusable digital twin technologies for any organisation, whether from the public or private sector, irrespective of size.

## License

This repository contains both source code and documentation, which are covered by different licenses:
- **Code:** Originally developed by Coefficient Systems, Ove Arup & Partners, and Informed Solutions, now maintained by National Digital Twin Programme. Licensed under the Apache License 2.0.
- **Documentation:** Licensed under the Open Government Licence v3.0.

See `LICENSE.md` for details. Service-specific notes remain in `frontend/README.md` and `backend/README.md`.

## Security and Responsible Disclosure

We take security seriously. If you believe you have found a security vulnerability in this repository, please follow our responsible disclosure process outlined in `SECURITY.md`.

## Software Bill of Materials (SBOM)

Download the [latest SBOM for this codebase](https://github.com/National-Digital-Twin/IRIS/dependency-graph/sbom) to view the current list of components used in this repository.

## Contributing

We welcome contributions that align with the Programme’s objectives. Please read `CONTRIBUTING.md` before submitting pull requests.

## Acknowledgements

For a list of acknowledgments, see `ACKNOWLEDGEMENTS.md`.

## Support and Contact

For questions or support, check Issues or contact the NDTP team on ndtp@businessandtrade.gov.uk.

**Maintained by the National Digital Twin Programme (NDTP).**

© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

Licensed under the NDTP InnerSource Licence – Version 1.0.
