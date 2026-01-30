# Changelog

**Repository:** `iris-api`\
**Description:** `Tracks all notable changes, version history, and roadmap toward 1.0.0 following Semantic Versioning.`\
**SPDX-License-Identifier:** `OGL-UK-3.0`

All notable changes to this repository will be documented in this file.
This project follows **Semantic Versioning (SemVer)** ([semver.org](https://semver.org/)), using the format:
`[MAJOR].[MINOR].[PATCH]`

- **MAJOR** (`X.0.0`) – Incompatible API/feature changes that break backward compatibility.
- **MINOR** (`0.X.0`) – Backward-compatible new features, enhancements, or functionality changes.
- **PATCH** (`0.0.X`) – Backward-compatible bug fixes, security updates, or minor corrections.
- **Pre-release versions** – Use suffixes such as `-alpha`, `-beta`, `-rc.1` (e.g., `2.1.0-beta.1`).
- **Build metadata** – If needed, use `+build` (e.g., `2.1.0+20250314`).

---

## [0.95.1] - 2026-01-14

- [NON-REQ]: updated indices to optimise for performance of the building feature charts

## [0.95.0] - 2026-01-12

### Features

- [NON-REQ]: added materialized view for analytics dashboard
- [DPAV-1779]: add endpoints for initial dashboard charts
- [DPAV-1779]: add endpoint for building fuel type chart
- [DPAV-1926]: updated and split the analytics view for dashboards
- [NON-REQ]: updated dashboard queries to reference renamed view
- [NON-REQ]: updated epc analytics view to include epc active field
- [NON-REQ]: added partial indices for base charts
- [NON-REQ]: added way to retrieve data for extreme weather chart
- [DPAV-1956]: updated view, query and routes to match extreme weather national dashboard spec
- [DPAV-1961]: added query and route to fetch data for the in date vs expired epc chart
- [DPAV-1951]: add covering index for historical EPC queries
- [DPAV-1951]: add active_snapshots to build_epc_analytics
- [DPAV-2060]: add database query timeout
- [DPAV-1951]: add building_epc_analytics_aggregates materialized view
- [DPAV-2060]: Ensure DEFAULT_QUERY_TIMEOUT is set with fallback
- [DPAV-1968]: add support for named areas dashboard
- [DPAV-1961]: support area filters on expired vs in-date epc
- [DPAV-1957]: add area columns to the extreme weather analytics view
- [DPAV-1970]: add active partial indices for building_epc_analytics table
- [DPAV-1970]: add composite partial index for fuel charts
- [DPAV-1963]: update dashboard building attributes endpoint
- [DPAV-1953]: add dashboard endpoint for epc over time chart
- [DPAV-2118]: combine Welsh regions
- [DPAV-1779]: New EPC charts
- [DPAV-1958] & [DPAV-1959]: add endpoints for grouped sap timeline charts
- [DPAV-2060]: reverted db query timeout back to 29 seconds

### Bug fixes

- [NON-REQ]: fixed down revision id to reference penultimate revision
- [NON-REQ]: added gpkg table to entrypoint script to fix data loading error
- [NON-REQ]: standardized index names across migrations
- [NON-REQ]: moved where statement to subquery to ngd attributes query
- [DPAV-2060]: fix execute_with_timeout reset
- [DPAV-1926]: changed the logic for geom matching to contains
- [DPAV-1926]: corrected the join logic in the sync region fk script

## [0.94.4] - 2025-10-24

- Fixed and removed visual overlap of region polygons introduced in 0.94.3.

## [0.94.3] - 2025-10-23

- Fixed issue with EPC analytics at the region level

## [0.94.2] - 2025-10-22

- [DPAV-1922] Updated EPC-related queries to fetch latest EPC records. Also added migration to update view definition for EPC analytics.
- [DPAV-1922] New migration to reduce time taken by regions materialized view refresh

## [0.94.1] - 2025-10-14

- [DPAV-1731] Added an `is_residential` flag to `iris.building` via Alembic migration to support distinguishing residential dwellings in downstream queries.
- Added OS NGD Buildings attributes to `/buildings/{uprn}`: roof material, solar panel presence, roof shape, and roof aspect areas (N, NE, E, SE, S, SW, W, NW, indeterminable).
- Added PostGIS fallback for NGD attributes when graph data is missing; extended mappers/DTOs accordingly.
- Included OS roof data in filterable buildings and filter summary; only include aspect directions with area > 0.
- New climate GeoJSON endpoints: `/data/climate/hot-summer-days`, `/data/climate/icing-days`, `/data/climate/wind-driven-rain`.
- Added underlying geometry data for Wales.

## [0.92.1] - 2025-07-22

- Updated changelog with note for release 0.92.0

## [0.92.0] - 2025-07-18

- Added query, mapper and route to the API to be able to query the main fuel type for a given dwelling

## [0.91.1] - 2025-07-15

- Fixed issue with grey buildings not being returned in the data
- Fixed issue with data discrepancy

## [0.91.0] - 2025-07-03

- Updated dependencies (2025-04-10)
- The `/buildings` endpoint has been updated to expect viewport coordinates (e.g. a minimum and maximum longitude and latitude) rather than a geohash. It then generates a polygon from these coordinates, which is then used to run a GeoSPARQL query on a named graph.
- The `/buildings/{uprn}` endpoint has been updated to run building-specific queries which fetch metadata about the roof, floors, walls etc. of the building.
- A new endpoint - `/epc-statistics/wards` - has been introduced, which queries a named graph to fetch the aggregated EPC statistics for the wards.
- A new `mappers.py` file has been introduced which exposes a set of functions mapping the responses received from the Secure Agent Graph to models.
- Added alembic with SQL migration scripts to enable PostGIS and create the IRIS schema
- Updated the bounding box query to fetch data from postgres
- Added a new filterable buildings endpoint to fetch data for filterable building in the user view port to power the filter functionality on the IRIS visualizer
- Added a filter summary endpoint to fetch a list of filters available in the users viewport to power the advanced filter panel functionality of the IRIS visualizer
- Added async support for alembic
- Added vault secrets for integration with RDS
- Optimized bounding box queries
- Added indices for EPC assessment and structure unit tables
- Added dev scripts to migrate data in CSVs on an s3 bucket to a postgres instance
- Fixed bug with the filter summary endpoint due to a missing none check on the postcode match
- Removed 404 response from the buildings/{uprn} endpoint to allow returning partial building data
- Fixed bug setting DEV_MODE to false in higher environments - affecting sign out and username display

## [0.90.1] – 2025-03-28

### Documentation

- Updated NOTICE.md with correct formatting
- Added endpoint to fetch user details
- Added endpoint to fetch sign out links

---

## [0.90.0] – 2025-03-28

### Initial Public Release (Pre-Stable)

This is the first public release of this repository under NDTP's open-source governance model.
Since this release is **pre-1.0.0**, changes may still occur that are **not fully backward-compatible**.

#### Initial Features

- View a choropleth map, summarising average EPC ratings per ward
- Search for a property via address
- Filter properties based on EPC rating, building type, postcode, drawn area and flagged status
- Filter properties based on further attributes (roof type, insulation type etc)
- View details (roof type, EPC rating, insulation type etc) of properties
- Download details of properties
- Flag a property to signal it's under investigation
- Unflagging a property with a rationale
- Viewing the reason why a property was unflagged

#### Known Limitations

- Some components are subject to change before `1.0.0`.
- APIs may evolve based on partner feedback and internal testing.

---

## Future Roadmap to `1.0.0`

The `0.90.x` series is part of NDTP’s **pre-stable development cycle**, meaning:

- **Minor versions (`0.91.0`, `0.92.0`...) introduce features and improvements** leading to a stable `1.0.0`.
- **Patch versions (`0.90.1`, `0.90.2`...) contain only bug fixes and security updates**.
- **Backward compatibility is NOT guaranteed until `1.0.0`**, though NDTP aims to minimise breaking changes.

Once `1.0.0` is reached, future versions will follow **strict SemVer rules**.

## Versioning Policy

1. **MAJOR updates (`X.0.0`)** – Typically introduce breaking changes that require users to modify their code or configurations.
   - **Breaking changes (default rule)**: Any backward-incompatible modifications require a major version bump.
   - **Non-breaking major updates (exceptional cases)**: A major version may also be incremented if the update represents a significant milestone, such as a shift in governance, a long-term stability commitment, or substantial new functionality that redefines the project’s scope.
2. **MINOR updates (`0.X.0`)** – New functionality that is backward-compatible.
3. **PATCH updates (`0.0.X`)** – Bug fixes, performance improvements, or security patches.
4. **Dependency updates** – A **major dependency upgrade** that introduces breaking changes should trigger a **MAJOR** version bump (once at `1.0.0`).

---

## How to Update This Changelog

1. When making changes, update this file under the **Unreleased** section.
2. Before a new release, move changes from **Unreleased** to a new dated section with a version number.
3. Follow **Semantic Versioning** rules to categorise changes correctly.
4. If pre-release versions are used, clearly mark them as `-alpha`, `-beta`, or `-rc.X`.

---

**Maintained by the National Digital Twin Programme (NDTP).**  
© Crown Copyright 2025. This work has been developed by the National Digital Twin Programme and is legally attributed to the Department for Business and Trade (UK) as the governing entity.  
Licensed under the Open Government Licence v3.0.  
For full licensing terms, see [OGL_LICENSE.md](OGL_LICENSE.md).
