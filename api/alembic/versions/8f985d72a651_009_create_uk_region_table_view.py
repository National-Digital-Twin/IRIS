# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""009_create_uk_region_table_view

Revision ID: 8f985d72a651
Revises: 2215b32f49a9
Create Date: 2025-08-26 13:48:42.927690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f985d72a651'
down_revision: Union[str, None] = '2215b32f49a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    """ Create id for iris.scotland_and_wales_region"""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.scotland_and_wales_region_fid_seq1
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )
   
    
    """ Create table for iris.scotland_and_wales_region"""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.scotland_and_wales_region
            ( 
                fid integer NOT NULL DEFAULT nextval('iris.scotland_and_wales_region_fid_seq1'::regclass),
                name character varying,
                area_code character varying,
                area_description character varying,
                file_name character varying,
                feature_serial_number integer,
                collection_serial_number integer,
                global_polygon_id integer,
                admin_unit_id integer,
                census_code character varying,
                hectares double precision,
                non_inland_area double precision,
                area_type_code character varying,
                area_type_description character varying,
                non_area_type_code character varying,
                non_area_type_description character varying,
                geometry geometry(MultiPolygon,4326),
                CONSTRAINT scotland_and_wales_region_P PRIMARY KEY (fid)
            )
    """
    )
    
    
    """ Create geo index for district_borough_unitary_ward"""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS scotland_and_wales_region_geometry_geom_idx
            ON iris.scotland_and_wales_region USING gist
            (geometry)
            TABLESPACE pg_default;
    """
    )
    """ Create id for english_region"""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.english_region_fid_seq1
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )
    """ Create table for iris.english_region"""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.english_region
            ( 
                fid integer NOT NULL DEFAULT nextval('iris.english_region_fid_seq1'::regclass),
                name character varying,
                area_code character varying,
                area_description character varying,
                file_name character varying,
                feature_serial_number integer,
                collection_serial_number integer,
                global_polygon_id integer,
                admin_unit_id integer,
                census_code character varying,
                hectares double precision,
                non_inland_area double precision,
                area_type_code character varying,
                area_type_description character varying,
                non_area_type_code character varying,
                non_area_type_description character varying,
                geometry geometry(MultiPolygon,4326),
                CONSTRAINT english_region_P PRIMARY KEY (fid)
            )
    """
    )
    
    
    """ Create geo index for english_region"""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS english_region_geometry_geom_idx
            ON iris.english_region USING gist
            (geometry)
            TABLESPACE pg_default;
    """
    )
    
    """ Create table uk_region"""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_region
            AS
            SELECT * FROM iris.scotland_and_wales_region
            UNION 
            SELECT * FROM iris.english_region;
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
            LEFT JOIN iris.uk_region b
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


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.uk_region_epc;
    """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.uk_region_geometry_geom_idx;
    """
    )

    op.execute(
        """
        DROP TABLE IF EXISTS iris.uk_region;
    """
    )
    op.execute(
        """
        DROP TABLE IF EXISTS iris.scotland_and_wales_region;
    """
    )
    op.execute(
        """
        DROP TABLE IF EXISTS iris.english_region;
    """
    )

    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.scotland_and_wales_region_fid_seq1;
    """
    )
    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.english_region_fid_seq1;
    """
    )
