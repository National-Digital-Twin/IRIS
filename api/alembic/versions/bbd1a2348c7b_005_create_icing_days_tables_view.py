# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""005_create_icing_days_tables_view

Revision ID: bbd1a2348c7b
Revises: 2599ec4b20bd
Create Date: 2025-08-14 15:19:20.548773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbd1a2348c7b'
down_revision: Union[str, None] = '2599ec4b20bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    """ Create sequence for icing days table primary key."""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.annual_count_of_icing_days_1991_2020_objectid_seq
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )
    
    
    """ Create table for icing days."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.annual_count_of_icing_days_1991_2020
            (
                objectid integer NOT NULL DEFAULT nextval('iris.annual_count_of_icing_days_1991_2020_objectid_seq'::regclass),
                icingdays double precision,
                shape geometry(MultiPolygon,4326),
                CONSTRAINT annual_count_of_icing_days_1991_2020_pkey PRIMARY KEY (objectid)
            )
    """
    )
    
    
    """ Alter sequence owner."""
    op.execute(
        """
        ALTER SEQUENCE iris.annual_count_of_icing_days_1991_2020_objectid_seq
            OWNED BY iris.annual_count_of_icing_days_1991_2020.objectid;
    """
    )
    
    
    """ Create index for icing days table."""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS annual_count_of_icing_days_1991_2020_shape_geom_idx
            ON iris.annual_count_of_icing_days_1991_2020 USING gist
            (shape)
            TABLESPACE pg_default;
    """
    )
    
    
    """ Create materialized view containing GeoJSON."""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.icing_days_geojson
            TABLESPACE pg_default
            AS
            SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(jsonb_build_object('type', 'Feature', 'geometry', st_asgeojson(shape)::json, 'properties', to_jsonb(t.*) - 'shape'::text))) AS geojson
            FROM iris.annual_count_of_icing_days_1991_2020 t
            WITH DATA;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.icing_days_geojson;
    """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.annual_count_of_icing_days_1991_2020_shape_geom_idx;
    """
    )

    op.execute(
        """
        DROP TABLE IF EXISTS iris.annual_count_of_icing_days_1991_2020;
    """
    )

    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.annual_count_of_icing_days_1991_2020_objectid_seq;
    """
    )