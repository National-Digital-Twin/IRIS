# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""019_update_building_epc_view

Revision ID: f7639f884c24
Revises: b55e05000f66
Create Date: 2025-10-16 12:35:56.419788

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f7639f884c24"
down_revision: Union[str, None] = "b55e05000f66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_epc_dependants() -> None:
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.uk_ward_epc;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.uk_ward_epc_data;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.uk_region_epc;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.uk_region_epc_data;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.district_borough_unitary_epc;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.district_borough_unitary_epc_data;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.boundary_line_ceremonial_counties_epc;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.boundary_line_ceremonial_counties_epc_data;
        """
    )


def _recreate_epc_dependants() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_ward_epc_data
            AS
            SELECT
                ward.name,
                COUNT(building.point) AS total,
                COUNT(CASE WHEN building.epc_rating = 'A' THEN 1 END) AS epc_a,
                COUNT(CASE WHEN building.epc_rating = 'B' THEN 1 END) AS epc_b,
                COUNT(CASE WHEN building.epc_rating = 'C' THEN 1 END) AS epc_c,
                COUNT(CASE WHEN building.epc_rating = 'D' THEN 1 END) AS epc_d,
                COUNT(CASE WHEN building.epc_rating = 'E' THEN 1 END) AS epc_e,
                COUNT(CASE WHEN building.epc_rating = 'F' THEN 1 END) AS epc_f,
                COUNT(CASE WHEN building.epc_rating = 'G' THEN 1 END) AS epc_g,
                COUNT(CASE WHEN building.epc_rating IS NULL THEN 1 END) AS epc_null,
                ward.geometry
            FROM iris.building_epc AS building
            LEFT JOIN iris.uk_ward AS ward
                ON ST_Intersects(ward.geometry, building.point)
            GROUP BY ward.name, ward.geometry
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_ward_epc
            AS
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features',
                jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', st_asgeojson(ST_SIMPLIFY(geometry, 0.0001))::json,
                        'properties', to_jsonb(t.*) - 'geometry'::text
                    )
                )
            ) AS geojson
            FROM iris.uk_ward_epc_data AS t
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_region_epc_data
            AS
            SELECT
                region.name,
                COUNT(building.point) AS total,
                COUNT(CASE WHEN building.epc_rating = 'A' THEN 1 END) AS epc_a,
                COUNT(CASE WHEN building.epc_rating = 'B' THEN 1 END) AS epc_b,
                COUNT(CASE WHEN building.epc_rating = 'C' THEN 1 END) AS epc_c,
                COUNT(CASE WHEN building.epc_rating = 'D' THEN 1 END) AS epc_d,
                COUNT(CASE WHEN building.epc_rating = 'E' THEN 1 END) AS epc_e,
                COUNT(CASE WHEN building.epc_rating = 'F' THEN 1 END) AS epc_f,
                COUNT(CASE WHEN building.epc_rating = 'G' THEN 1 END) AS epc_g,
                COUNT(CASE WHEN building.epc_rating IS NULL THEN 1 END) AS epc_null,
                region.geometry
            FROM iris.building_epc AS building
            LEFT JOIN iris.uk_region AS region
                ON ST_Intersects(region.geometry, building.point)
            GROUP BY region.name, region.geometry
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_region_epc
            AS
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features',
                jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', st_asgeojson(ST_SIMPLIFY(geometry, 0.0001))::json,
                        'properties', to_jsonb(t.*) - 'geometry'::text
                    )
                )
            ) AS geojson
            FROM iris.uk_region_epc_data AS t
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.district_borough_unitary_epc_data
            AS
            SELECT
                district.name,
                COUNT(building.point) AS total,
                COUNT(CASE WHEN building.epc_rating = 'A' THEN 1 END) AS epc_a,
                COUNT(CASE WHEN building.epc_rating = 'B' THEN 1 END) AS epc_b,
                COUNT(CASE WHEN building.epc_rating = 'C' THEN 1 END) AS epc_c,
                COUNT(CASE WHEN building.epc_rating = 'D' THEN 1 END) AS epc_d,
                COUNT(CASE WHEN building.epc_rating = 'E' THEN 1 END) AS epc_e,
                COUNT(CASE WHEN building.epc_rating = 'F' THEN 1 END) AS epc_f,
                COUNT(CASE WHEN building.epc_rating = 'G' THEN 1 END) AS epc_g,
                COUNT(CASE WHEN building.epc_rating IS NULL THEN 1 END) AS epc_null,
                district.geometry
            FROM iris.building_epc AS building
            LEFT JOIN iris.district_borough_unitary AS district
                ON ST_Intersects(district.geometry, building.point)
            GROUP BY district.name, district.geometry
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.district_borough_unitary_epc
            AS
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features',
                jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', st_asgeojson(ST_SIMPLIFY(geometry, 0.0001))::json,
                        'properties', to_jsonb(t.*) - 'geometry'::text
                    )
                )
            ) AS geojson
            FROM iris.district_borough_unitary_epc_data AS t
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.boundary_line_ceremonial_counties_epc_data
            AS
            SELECT
                county.name,
                COUNT(building.point) AS total,
                COUNT(CASE WHEN building.epc_rating = 'A' THEN 1 END) AS epc_a,
                COUNT(CASE WHEN building.epc_rating = 'B' THEN 1 END) AS epc_b,
                COUNT(CASE WHEN building.epc_rating = 'C' THEN 1 END) AS epc_c,
                COUNT(CASE WHEN building.epc_rating = 'D' THEN 1 END) AS epc_d,
                COUNT(CASE WHEN building.epc_rating = 'E' THEN 1 END) AS epc_e,
                COUNT(CASE WHEN building.epc_rating = 'F' THEN 1 END) AS epc_f,
                COUNT(CASE WHEN building.epc_rating = 'G' THEN 1 END) AS epc_g,
                COUNT(CASE WHEN building.epc_rating IS NULL THEN 1 END) AS epc_null,
                county.geometry
            FROM iris.building_epc AS building
            LEFT JOIN iris.boundary_line_ceremonial_counties AS county
                ON ST_Intersects(county.geometry, building.point)
            GROUP BY county.name, county.geometry
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.boundary_line_ceremonial_counties_epc
            AS
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features',
                jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', st_asgeojson(ST_SIMPLIFY(geometry, 0.0001))::json,
                        'properties', to_jsonb(t.*) - 'geometry'::text
                    )
                )
            ) AS geojson
            FROM iris.boundary_line_ceremonial_counties_epc_data AS t
        WITH NO DATA;
        """
    )


def _set_application_name() -> None:
    op.execute(
        sa.text(
            "SET LOCAL application_name = 'alembic_019_update_building_epc_view';"
        )
    )


def upgrade() -> None:
    """Upgrade schema."""

    _set_application_name()
    _drop_epc_dependants()
    op.execute(
        """
        DROP INDEX IF EXISTS idx_building_epc_geom;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.building_epc AS
        SELECT
            bld.uprn,
            latest.epc_rating,
            bld.point
        FROM iris.building AS bld
        LEFT JOIN LATERAL (
            SELECT
                assess.id,
                assess.uprn,
                assess.epc_rating,
                assess.lodgement_date
            FROM iris.epc_assessment AS assess
            WHERE assess.uprn = bld.uprn
            ORDER BY
                assess.lodgement_date DESC NULLS LAST,
                assess.id DESC
            LIMIT 1
        ) AS latest ON TRUE
        WHERE bld.is_residential IS TRUE
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_building_epc_geom
            ON iris.building_epc
            USING GIST (point);
        """
    )
    _recreate_epc_dependants()


def downgrade() -> None:
    """Downgrade schema."""

    _set_application_name()
    _drop_epc_dependants()
    op.execute(
        """
        DROP INDEX IF EXISTS idx_building_epc_geom;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc;
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.building_epc AS
        SELECT
            building.uprn,
            assessment.epc_rating,
            building.point
        FROM iris.building AS building
        LEFT JOIN iris.epc_assessment AS assessment
            ON building.uprn = assessment.uprn
        WHERE building.is_residential IS TRUE
        WITH NO DATA;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_building_epc_geom
            ON iris.building_epc
            USING GIST (point);
        """
    )
    _recreate_epc_dependants()

