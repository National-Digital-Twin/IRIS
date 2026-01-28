# README

**Repository:** `iris-api`\
**Description:** `This repository functions as the backend of IRIS and contains API routes that serve and process data to/from the frontend`\
**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0 `

## Overview

IRIS is a digital tool designed to support data-driven decision-making for retrofitting domestic properties by identifying homes that could benefit from energy efficiency improvements. It enables stakeholders to assess housing stock based on energy performance data to help target funding schemes and policy interventions more effectively. IRIS is part of the NDTP Demonstrator Programme. This repository functions as one of the core API services for the IRIS visualization application. It provides the neccessary REST styled endpoints to serve and route data to and from the IRIS visualization application.

## Prerequisites

Before using this repository, ensure you have the following dependencies installed:

- **Required Tooling:**
  - Python version 3.12.0
  - Docker
  - make
  - Git
- **Pipeline Requirements:**
  - GitHub actions
- **System Requirements:**
  - Dual-Core CPU (Intel i5 or AMD Ryzen 3 equivalent), 8GB RAM, SSD/HDD with 10GB free space

## Quick Start

Follow these steps to get started quickly with this repository. For detailed installation, configuration, and deployment, refer to the relevant MD files.

### 1. Download and Build

```sh
git clone https://github.com/National-Digital-Twin/iris-api.git
cd iris-api
```

### 2. Install dependencies

```sh
pip install -f requirements.txt
```

### 3. Run Build Version

```sh
make run-api
```

### 3. Full Installation

Refer to [INSTALLATION.md](INSTALLATION.md) for detailed installation steps, including required dependencies and setup configurations.

### 4. Uninstallation

For steps to remove this repository and its dependencies, see [UNINSTALL.md](UNINSTALL.md).

## Features

- **Core functionality** Provides API routes that server and route data to and from the IRIS visualizer application.
- **Key integrations** Provides REST interface to QUERY and WRITE data to the IA node.
- **Scalability & performance** Optimized for scalability and performance.

## API Documentation

The API documentation can be accessed by running the application and navigation to the `/api-docs` endpoint. For open API docs please navigate to `/api-docs/openapi.json`.

## Public Funding Acknowledgment

This repository has been developed with public funding as part of the National Digital Twin Programme (NDTP), a UK Government initiative. NDTP, alongside its partners, has invested in this work to advance open, secure, and reusable digital twin technologies for any organisation, whether from the public or private sector, irrespective of size.

## License

This repository contains both source code and documentation, which are covered by different licenses:
- **Code:** Originally developed by Coefficient Systems and Informed Solutions, now maintained by National Digital Twin Programme. Licensed under the Apache License 2.0.
- **Documentation:** Licensed under the Open Government Licence v3.0.

See `LICENSE.md`, `OGL_LICENCE.md`, and `NOTICE.md` for details.

## Security and Responsible Disclosure

We take security seriously. If you believe you have found a security vulnerability in this repository, please follow our responsible disclosure process outlined in `SECURITY.md`.

## Contributing

We welcome contributions that align with the Programme’s objectives. Please read our `CONTRIBUTING.md` guidelines before submitting pull requests.

## Acknowledgements

This repository has benefited from collaboration with various organisations. For a list of acknowledgments, see `ACKNOWLEDGEMENTS.md`.

## Support and Contact

For questions or support, check our Issues or contact the NDTP team on ndtp@businessandtrade.gov.uk.

**Maintained by the National Digital Twin Programme (NDTP).**

© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
