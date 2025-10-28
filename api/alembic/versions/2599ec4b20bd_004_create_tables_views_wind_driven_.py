# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""004_create_tables_views_wind_driven_rain

Revision ID: 2599ec4b20bd
Revises: d12ce7dc9019
Create Date: 2025-08-11 17:38:06.036314

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2599ec4b20bd"
down_revision: Union[str, None] = "d12ce7dc9019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    """ Create table for wind-driven rain."""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.wind_driven_rain_projections_objectid_seq
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.wind_driven_rain_projections
        (
            objectid integer NOT NULL DEFAULT nextval('iris.wind_driven_rain_projections_objectid_seq'::regclass),
            wall_orientation integer,
            wdr_baseline_lower double precision,
            wdr_baseline_median double precision,
            wdr_baseline_upper double precision,
            wdr_20_lower double precision,
            wdr_20_median double precision,
            wdr_20_upper double precision,
            wdr_40_lower double precision,
            wdr_40_median double precision,
            wdr_40_upper double precision,
            x_coord double precision,
            y_coord double precision,
            shape geometry(MultiPolygon,4326),
            CONSTRAINT wind_driven_rain_projections__pkey PRIMARY KEY (objectid)
        )
    """
    )

    op.execute(
        """
        ALTER SEQUENCE iris.wind_driven_rain_projections_objectid_seq
            OWNED BY iris.wind_driven_rain_projections.objectid;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS wind_driven_rain_projections_shape_idx
            ON iris.wind_driven_rain_projections USING gist
            (shape)
            TABLESPACE pg_default;
    """
    )

    """Create views for wind-driven rain."""

    op.execute(
        """
        CREATE OR REPLACE VIEW iris.median_projections_per_shape
            AS
            SELECT x_coord,
                y_coord,
                max(shape::text) AS shape,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 0) AS wdr20_0,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 0) AS wdr40_0,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 45) AS wdr20_45,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 45) AS wdr40_45,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 90) AS wdr20_90,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 90) AS wdr40_90,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 135) AS wdr20_135,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 135) AS wdr40_135,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 180) AS wdr20_180,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 180) AS wdr40_180,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 225) AS wdr20_225,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 225) AS wdr40_225,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 270) AS wdr20_270,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 270) AS wdr40_270,
                max(wdr_20_median) FILTER (WHERE wall_orientation = 315) AS wdr20_315,
                max(wdr_40_median) FILTER (WHERE wall_orientation = 315) AS wdr40_315
            FROM iris.wind_driven_rain_projections
            GROUP BY x_coord, y_coord;
    """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.wind_driven_rain_projections_geojson
        TABLESPACE pg_default
        AS
            SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(jsonb_build_object('type', 'Feature', 'geometry', st_asgeojson(shape)::json, 'properties', to_jsonb(t.*) - 'geom'::text))) AS geojson
            FROM iris.median_projections_per_shape t
        WITH DATA;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.wind_driven_rain_projections_geojson;
    """
    )

    op.execute(
        """
        DROP VIEW iris.median_projections_per_shape;
    """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.wind_driven_rain_projections_shape_idx;
    """
    )

    op.execute(
        """
        DROP TABLE IF EXISTS iris.wind_driven_rain_projections CASCADE;
    """
    )

    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.wind_driven_rain_projections_objectid_seq;
    """
    )
