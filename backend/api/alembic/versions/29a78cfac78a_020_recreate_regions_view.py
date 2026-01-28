# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""020_recreate_regions_view

Revision ID: 29a78cfac78a
Revises: f7639f884c24
Create Date: 2025-10-23 15:45:36.986302

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "29a78cfac78a"
down_revision: Union[str, None] = "f7639f884c24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    """ Add simplified geometry column to english_region table"""
    op.execute(
        """
        ALTER TABLE iris.english_region ADD COLUMN IF NOT EXISTS geom_simplified geometry;
    """
    )

    """ Update column to add simplified geometry"""
    op.execute(
        """
        UPDATE iris.english_region SET geom_simplified = ST_Simplify(geometry, 0.0001);
    """
    )

    """ Create index for simplified geometry column"""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS english_region_geom_simplified_idx ON iris.english_region USING gist (geom_simplified);
    """
    )

    """ Recreate materialised views for regions"""
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
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_region_epc_data
        AS
        WITH regions AS (
                SELECT name, geom_simplified AS geometry
                FROM iris.english_region
                UNION ALL
                SELECT name, ST_Simplify(geometry, 0.0001) AS geometry
                FROM iris.country_region
                WHERE name = 'Wales'
            )
            SELECT
                r.name AS name,
                SUM(e.total) AS total,
                SUM(e.epc_a) AS epc_a,
                SUM(e.epc_b) AS epc_b,
                SUM(e.epc_c) AS epc_c,
                SUM(e.epc_d) AS epc_d,
                SUM(e.epc_e) AS epc_e,
                SUM(e.epc_f) AS epc_f,
                SUM(e.epc_g) AS epc_g,
                SUM(e.epc_null) AS epc_null,
                r.geometry
            FROM regions r
            JOIN iris.district_borough_unitary_epc_data e
            ON ST_Contains(r.geometry, ST_Simplify(e.geometry, 0.0001))
            GROUP BY r.name, r.geometry
        WITH NO DATA;
    """
    )

    """ Create materialized view containing GeoJSON."""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_region_epc
            TABLESPACE pg_default
            AS
            SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(jsonb_build_object('type', 'Feature', 'geometry', st_asgeojson(ST_SIMPLIFY(geometry, 0.0001))::json, 'properties', to_jsonb(t.*) - 'geometry'::text))) AS geojson
            FROM iris.uk_region_epc_data t
            WITH NO DATA;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    """ Recreate materialised views for regions"""
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
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_region_epc_data
            AS
            SELECT
                b.name,
                COUNT (a.point) AS total,
                COUNT(CASE WHEN a.epc_rating = 'A' THEN 1 END) AS epc_a,
                COUNT(CASE WHEN a.epc_rating = 'B' THEN 1 END) AS epc_b,
                COUNT(CASE WHEN a.epc_rating = 'C' THEN 1 END) AS epc_c,
                COUNT(CASE WHEN a.epc_rating = 'D' THEN 1 END) AS epc_d,
                COUNT(CASE WHEN a.epc_rating = 'E' THEN 1 END) AS epc_e,
                COUNT(CASE WHEN a.epc_rating = 'F' THEN 1 END) AS epc_f,
                COUNT(CASE WHEN a.epc_rating = 'G' THEN 1 END) AS epc_g,
                COUNT(CASE WHEN a.epc_rating IS NULL THEN 1 END) AS epc_null,
                b.geometry
            FROM iris.building_epc a
            LEFT JOIN iris.english_region b
            ON ST_Intersects(b.geometry, a.point)
            GROUP BY b.name, b.geometry
        WITH NO DATA;
    """
    )

    """ Create materialized view containing GeoJSON."""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_region_epc
            TABLESPACE pg_default
            AS
            SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(jsonb_build_object('type', 'Feature', 'geometry', st_asgeojson(ST_SIMPLIFY(geometry, 0.0001))::json, 'properties', to_jsonb(t.*) - 'geometry'::text))) AS geojson
            FROM iris.uk_region_epc_data t
            WITH NO DATA;
    """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS english_region_geom_simplified_idx;
    """
    )

    op.execute(
        """
        ALTER TABLE iris.english_region DROP COLUMN IF EXISTS geom_simplified geometry;
    """
    )
