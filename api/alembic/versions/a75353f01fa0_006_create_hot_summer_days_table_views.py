# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""006_create_hot_summer_days_table_views

Revision ID: a75353f01fa0
Revises: bbd1a2348c7b
Create Date: 2025-08-18 10:52:55.528477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a75353f01fa0'
down_revision: Union[str, None] = 'bbd1a2348c7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    """ Create table for hot summer days."""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.annual_count_of_hot_summer_days_projections_12km_objectid_seq
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )
    
    
    """ Create table for hot summer days."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.annual_count_of_hot_summer_days_projections_12km
        (
            objectid integer NOT NULL DEFAULT nextval('iris.annual_count_of_hot_summer_days_projections_12km_objectid_seq'::regclass),
            latitude double precision,
            longitude double precision,
            projection_y_coordinate double precision,
            projection_x_coordinate double precision,
            hsd_baseline_81_00_lower double precision,
            hsd_baseline_81_00_median double precision,
            hsd_baseline_81_00_upper double precision,
            hsd_baseline_01_20_lower double precision,
            hsd_baseline_01_20_median double precision,
            hsd_baseline_01_20_upper double precision,
            hsd_15_lower double precision,
            hsd_15_median double precision,
            hsd_15_upper double precision,
            hsd_20_lower double precision,
            hsd_20_median double precision,
            hsd_20_upper double precision,
            hsd_25_lower double precision,
            hsd_25_median double precision,
            hsd_25_upper double precision,
            hsd_30_lower double precision,
            hsd_30_median double precision,
            hsd_30_upper double precision,
            hsd_40_lower double precision,
            hsd_40_median double precision,
            hsd_40_upper double precision,
            shape geometry(MultiPolygon,3857),
            CONSTRAINT annual_count_of_hot_summer_days_projections_12km_pkey PRIMARY KEY (objectid)
        )
    """
    )


    """ Alter sequence owner."""
    op.execute(
        """
        ALTER SEQUENCE iris.annual_count_of_hot_summer_days_projections_12km_objectid_seq
            OWNED BY iris.annual_count_of_hot_summer_days_projections_12km.objectid;
    """
    )
    
    
    """ Create index for hot summer days table."""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS annual_count_of_hot_summer_days_projections_12km_shape_geom_idx
            ON iris.annual_count_of_hot_summer_days_projections_12km USING gist
            (shape)
            TABLESPACE pg_default;
    """
    )
    
    
    """ Create materialized view containing GeoJSON."""
    op.execute(
        """
        CREATE OR REPLACE VIEW iris.median_summer_days_per_projection
            AS
            SELECT objectid, latitude, longitude, hsd_baseline_01_20_median, hsd_15_median, hsd_20_median, hsd_25_median, hsd_30_median, hsd_40_median, shape
            FROM iris.annual_count_of_hot_summer_days_projections_12km;
    """
    )
    
    
    """ Create materialized view containing GeoJSON."""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.hot_summer_days_geojson
            TABLESPACE pg_default
            AS
            SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(jsonb_build_object('type', 'Feature', 'geometry', st_asgeojson(shape)::json, 'properties', to_jsonb(t.*) - 'shape'::text))) AS geojson
            FROM iris.median_summer_days_per_projection t
            WITH DATA;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.hot_summer_days_days_geojson;
    """
    )

    op.execute(
        """
        DROP VIEW IF EXISTS iris.median_summer_days_per_projection;
    """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.annual_count_of_hot_summer_days_projections_12km_shape_geom_idx;    """
    )

    op.execute(
        """
        DROP TABLE IF EXISTS iris.annual_count_of_hot_summer_days_projections_12km;
    """
    )

    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.annual_count_of_hot_summer_days_projections_12km_objectid_seq;
    """
    )
