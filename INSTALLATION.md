# INSTALLATION

**Repository:** `IRIS`  
**Description:** `Combined installation instructions for the IRIS frontend and backend services.`  
**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0`

## Overview

This monorepo contains:
- `frontend/` — IRIS visualisation client (Angular).
- `backend/` — IRIS API service (Python).

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

## Licensing

See `LICENSE.md` for full licensing terms.

© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
