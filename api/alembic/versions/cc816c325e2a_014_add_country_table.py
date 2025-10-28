# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""014_add_country_table

Revision ID: cc816c325e2a
Revises: cf408e1ffd0e
Create Date: 2025-09-10 10:40:29.793570

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cc816c325e2a"
down_revision: Union[str, None] = "cf408e1ffd0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    """ Create table for country regions."""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.country_region_fid_seq
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )

    """ Create table for country_region."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.country_region
        (
            fid integer NOT NULL DEFAULT nextval('iris.country_region_fid_seq'::regclass),
            name character varying(100),
            area_code character varying(3),
            area_description character varying(50),
            file_name character varying(100),
            feature_serial_number integer,
            collection_serial_number integer NOT NULL,
            global_polygon_id integer NOT NULL,
            admin_unit_id integer NOT NULL,
            census_code character varying(9),
            hectares double precision NOT NULL,
            non_inland_area double precision NOT NULL,
            area_type_code character varying(2) NOT NULL,
            area_type_description character varying(25)NOT NULL,
            non_area_type_code character varying(3),
            non_area_type_description character varying(36),
            geometry geometry(MultiPolygon,4326) NOT NULL,
            CONSTRAINT country_region_pkey PRIMARY KEY (fid)
        )
    """
    )

    """ Alter sequence owner."""
    op.execute(
        """
        ALTER SEQUENCE iris.country_region_fid_seq
            OWNED BY iris.country_region.fid;
    """
    )

    """ Create index for country_region table."""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS country_region_geometry_idx
            ON iris.country_region USING gist
            (geometry)
            TABLESPACE pg_default;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP INDEX IF EXISTS iris.country_region_geometry_idx;    """
    )

    op.execute(
        """
        DROP TABLE IF EXISTS iris.country_region;
    """
    )

    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.country_region_fid_seq;
    """
    )
