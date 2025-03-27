# README

**Repository:** `IRIS-data-cleanser`  
**Description:** `This repository contains an ETL pipeline which uses Airbyte to import data into Postgres, dbt for data transformation and eventual upload of data in CSV format to S3.`  
**SPDX-License-Identifier:** `Apache-2.0 AND OGL-UK-3.0 `

## Overview
IRIS is a digital tool designed to support data-driven decision-making for retrofitting domestic properties by identifying homes that could benefit from energy efficiency improvements. It enables stakeholders to assess housing stock based on energy performance data to help target funding schemes and policy interventions more effectively. IRIS is part of the NDTP Demonstrator Programme.

This repository is an ETL pipeline which fetches and transforms EPC and OS data, used by the IRIS demonstrator.

## Prerequisites
Before using this repository, ensure you have the following dependencies installed:
- **Required Tooling:** Airbyte, dbt, Python
- **Pipeline Requirements:** N/A
- **Supported Kubernetes Versions:** N/A
- **System Requirements:** Dual-Core CPU (Intel i5 or AMD Ryzen 3 equivalent), 8GB RAM, SSD/HDD with 10GB free space

## Quick Start
Follow these steps to get started quickly with this repository. For detailed installation, configuration, and deployment, refer to the relevant MD files.

### 1. Download and Build
```sh
git clone https://github.com/IRIS-data-cleanser.git
cd IRIS-data-cleanser
```

### 2. Run Build Version
```sh
poetry --version
```

### 3. Full Installation
Refer to [INSTALLATION.md](INSTALLATION.md) for detailed installation steps, including required dependencies and setup configurations.

### 4. Uninstallation
For steps to remove this repository and its dependencies, see [UNINSTALL.md](UNINSTALL.md).

## Features
This repository contains the following significant features:
- Airbyte configurations to extract EPC data from the EPC Open Data API and OS API
- dbt scripts to perform data transformation on the source data and upload to S3

## Public Funding Acknowledgment
This repository has been developed with public funding as part of the National Digital Twin Programme (NDTP), a UK Government initiative. NDTP, alongside its partners, has invested in this work to advance open, secure, and reusable digital twin technologies for any organisation, whether from the public or private sector, irrespective of size.

## License
This repository contains both source code and documentation, which are covered by different licenses:
- **Code:** Originally developed by [Original Developer, if applicable], now maintained by National Digital Twin Programme. Licensed under the Apache License 2.0.
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
