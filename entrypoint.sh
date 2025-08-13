#!/bin/bash
set -e

alembic upgrade head
GPKG_SOURCE=https://services.arcgis.com/Lq3V5RFuTBC9I7kv/arcgis/rest/services/Annual_Index_of_Wind_Driven_Rain_Projections_5km/FeatureServer/replicafilescache/Annual_Index_of_Wind_Driven_Rain_Projections_5km_-6134910210859057092.gpkg  python load_gpkg_to_postgis.py

python api/main.py --host 0.0.0.0