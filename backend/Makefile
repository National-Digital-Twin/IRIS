docker-build:
	docker build --no-cache --secret id=pat_token,env=GITHUB_ACCESS_TOKEN -t iris/write-api:latest .

docker-run:
	docker run -d --rm --name iris-write-api --network developer-resources_iris -e PORT=3010 -e DEV=True -e JENA_PROTOCOL=http -e JENA_URL=127.0.0.1 -e JENA_PORT:3030 -e DB_HOST=postgis -p 3010:3010 iris/write-api:latest

run-api:
	python developer-resources/sync_region_fks_dbu.py
	python api/main.py

test:
	python -m pytest

load-met-office-data:
	MATERIALIZED_VIEW=iris.wind_driven_rain_projections_geojson TARGET_TABLE=wind_driven_rain_projections GPKG_SOURCE=https://services.arcgis.com/Lq3V5RFuTBC9I7kv/arcgis/rest/services/Annual_Index_of_Wind_Driven_Rain_Projections_5km/FeatureServer/replicafilescache/Annual_Index_of_Wind_Driven_Rain_Projections_5km_-6134910210859057092.gpkg GPKG_TABLE=Annual_Index_of_Wind_Driven_Rain___Projections__5km_ python developer-resources/load_gpkg_to_postgis.py
	MATERIALIZED_VIEW=iris.icing_days_geojson TARGET_TABLE=annual_count_of_icing_days_1991_2020 GPKG_SOURCE=https://services.arcgis.com/Lq3V5RFuTBC9I7kv/arcgis/rest/services/Annual_Count_of_Icing_Days_1991_2020/FeatureServer/replicafilescache/Annual_Count_of_Icing_Days_1991_2020_5977951113111576455.gpkg GPKG_TABLE=annual_count_of_icing_days_1991_2020 python developer-resources/load_gpkg_to_postgis.py
	MATERIALIZED_VIEW=iris.hot_summer_days_geojson TARGET_TABLE=annual_count_of_hot_summer_days_projections_12km GPKG_SOURCE=https://services.arcgis.com/Lq3V5RFuTBC9I7kv/arcgis/rest/services/Annual_Count_of_Hot_Days___Projections__12km_grid_/FeatureServer/replicafilescache/Annual_Count_of_Hot_Days___Projections__12km_grid__5151054028377652076.gpkg GPKG_TABLE=annual_count_of_hot_summer_days_projections_12km python developer-resources/load_gpkg_to_postgis.py

load-epc-data:
	JOIN_VIEW=iris.uk_ward DATA_VIEW=iris.uk_ward_epc_data MATERIALIZED_VIEW=iris.uk_ward_epc TARGET_TABLE=district_borough_unitary_ward GPKG_SOURCE=https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect GPKG_TABLE=district_borough_unitary_ward python developer-resources/load_gpkg_to_postgis.py
	JOIN_VIEW=iris.uk_ward DATA_VIEW=iris.uk_ward_epc_data MATERIALIZED_VIEW=iris.uk_ward_epc TARGET_TABLE=unitary_electoral_division GPKG_SOURCE=https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect GPKG_TABLE=unitary_electoral_division python developer-resources/load_gpkg_to_postgis.py
	JOIN_VIEW=iris.uk_region DATA_VIEW=iris.uk_region_epc_data MATERIALIZED_VIEW=iris.uk_region_epc TARGET_TABLE=scotland_and_wales_region GPKG_SOURCE=https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect GPKG_TABLE=scotland_and_wales_region python developer-resources/load_gpkg_to_postgis.py
	JOIN_VIEW=iris.uk_region DATA_VIEW=iris.uk_region_epc_data MATERIALIZED_VIEW=iris.uk_region_epc TARGET_TABLE=english_region GPKG_SOURCE=https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect GPKG_TABLE=english_region python developer-resources/load_gpkg_to_postgis.py
	DATA_VIEW=iris.district_borough_unitary_epc_data MATERIALIZED_VIEW=iris.district_borough_unitary_epc TARGET_TABLE=district_borough_unitary GPKG_SOURCE=https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect GPKG_TABLE=district_borough_unitary python developer-resources/load_gpkg_to_postgis.py
	DATA_VIEW=iris.boundary_line_ceremonial_counties_epc_data MATERIALIZED_VIEW=iris.boundary_line_ceremonial_counties_epc TARGET_TABLE=boundary_line_ceremonial_counties GPKG_SOURCE=https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect GPKG_TABLE=boundary_line_ceremonial_counties python developer-resources/load_gpkg_to_postgis.py

load-country:
	TARGET_TABLE=country_region GPKG_SOURCE='https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect' GPKG_TABLE=country_region python developer-resources/load_gpkg_to_postgis.py

load-counties:
	TARGET_TABLE=boundary_line_ceremonial_counties GPKG_SOURCE='https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect' GPKG_TABLE=boundary_line_ceremonial_counties python developer-resources/load_gpkg_to_postgis.py

load-districts:
	TARGET_TABLE=district_borough_unitary GPKG_SOURCE='https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect' GPKG_TABLE=district_borough_unitary python developer-resources/load_gpkg_to_postgis.py
	python developer-resources/sync_region_fks_dbu.py

load-english-region:
	TARGET_TABLE=english_region GPKG_SOURCE='https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect' GPKG_TABLE=english_region python developer-resources/load_gpkg_to_postgis.py

load-scotland-and-wales-region:
	TARGET_TABLE=scotland_and_wales_region GPKG_SOURCE='https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect' GPKG_TABLE=scotland_and_wales_region python developer-resources/load_gpkg_to_postgis.py

load-wards:
	TARGET_TABLE=district_borough_unitary_ward GPKG_SOURCE='https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect' GPKG_TABLE=district_borough_unitary_ward  python developer-resources/load_gpkg_to_postgis.py
	TARGET_TABLE=unitary_electoral_division GPKG_SOURCE='https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=GeoPackage&redirect' GPKG_TABLE=unitary_electoral_division python developer-resources/load_gpkg_to_postgis.py

migrate:
	alembic upgrade head

iris-api-resources-up:
	docker compose -f developer-resources/docker-compose.yml up -d

iris-api-resources-down:
	docker compose -f developer-resources/docker-compose.yml down
