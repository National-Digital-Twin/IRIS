# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""038_create_sunlight_hours_table_views

Revision ID: d19f556331db
Revises: b909c053aea6
Create Date: 2026-02-04 12:27:26.700587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd19f556331db'
down_revision: Union[str, None] = 'b909c053aea6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    """ Create table for sunlight hours."""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.average_annual_count_of_sunlight_hours_5km_objectid_seq
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )

    """ Create table for sunlight hours."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.average_annual_count_of_sunlight_hours_5km
        (
            objectid integer NOT NULL DEFAULT nextval('iris.average_annual_count_of_sunlight_hours_5km_objectid_seq'::regclass),
            sunlight_hours double precision,
            latitude double precision,
            longitude double precision,
            projection_x_coordinate double precision,
            projection_y_coordinate double precision,
            shape_wkt text,
            shape geometry(Polygon, 4326),
            CONSTRAINT average_annual_count_of_sunlight_hours_5km_pkey PRIMARY KEY (objectid)
        )
    """
    )

    """ Alter sequence owner."""
    op.execute(
        """
        ALTER SEQUENCE iris.average_annual_count_of_sunlight_hours_5km_objectid_seq
            OWNED BY iris.average_annual_count_of_sunlight_hours_5km.objectid;
    """
    )

    """ Create materialized view containing GeoJSON."""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.annual_average_sunlight_hours_geojson
            TABLESPACE pg_default
            AS
            SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(jsonb_build_object('type', 'Feature', 'geometry', st_asgeojson(shape)::json, 'properties', to_jsonb(t.*) - 'shape'::text))) AS geojson
            FROM iris.average_annual_count_of_sunlight_hours_5km t
            WITH DATA;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS average_annual_count_of_sunlight_hours_5km_shape_idx
        ON iris.average_annual_count_of_sunlight_hours_5km
        USING GIST (shape);
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP INDEX IF EXISTS iris.average_annual_count_of_sunlight_hours_5km_shape_idx;
    """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.average_sunlight_hours_geojson;
    """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.average_annual_count_of_sunlight_hours_5km_shape_idx;    """
    )

    op.execute(
        """
        DROP TABLE IF EXISTS iris.average_annual_count_of_sunlight_hours_5km;
    """
    )

    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.average_annual_count_of_sunlight_hours_5km_objectid_seq;
    """
    )
