# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""008_create_uk_ward_table_view

Revision ID: 2215b32f49a9
Revises: a75353f01fa0
Create Date: 2025-08-19 16:01:44.272631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2215b32f49a9'
down_revision: Union[str, None] = 'a75353f01fa0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    """ Create lookup table building_epc"""
    op.execute(
        """   
   	CREATE INDEX IF NOT EXISTS idx_building_uprn ON iris.building(uprn);
    """
    )
    op.execute(
        """
   	CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_epc AS
        SELECT a.uprn, b.epc_rating, a.point
        FROM iris.building a
        LEFT JOIN iris.epc_assessment b
        ON a.uprn = b.uprn;
    """
    )        

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_building_epc_geom
        ON iris.building_epc
        USING GIST (point);
    """
    )  
    """ Create id for iris.district_borough_unitary_ward"""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.district_borough_unitary_ward_fid_seq1
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )
   
    
    """ Create table for iris.district_borough_unitary_ward"""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.district_borough_unitary_ward
            ( 
                fid integer NOT NULL DEFAULT nextval('iris.district_borough_unitary_ward_fid_seq1'::regclass),
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
                CONSTRAINT district_borough_unitary_ward_P PRIMARY KEY (fid)
            )
    """
    )
    
    
    """ Create geo index for district_borough_unitary_ward"""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS district_borough_unitary_ward_geometry_geom_idx
            ON iris.district_borough_unitary_ward USING gist
            (geometry)
            TABLESPACE pg_default;
    """
    )
    """ Create id for unitary_electoral_division"""
    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS iris.unitary_electoral_division_fid_seq1
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
    """
    )
    """ Create table for iris.unitary_electoral_division"""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS iris.unitary_electoral_division
            ( 
                fid integer NOT NULL DEFAULT nextval('iris.unitary_electoral_division_fid_seq1'::regclass),
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
                CONSTRAINT unitary_electoral_division_P PRIMARY KEY (fid)
            )
    """
    )
    
    
    """ Create geo index for unitary_electoral_division"""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS unitary_electoral_division_geometry_geom_idx
            ON iris.unitary_electoral_division USING gist
            (geometry)
            TABLESPACE pg_default;
    """
    )
    
    """ Create table uk_ward"""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_ward
            AS
            SELECT * FROM iris.district_borough_unitary_ward
            UNION 
            SELECT * FROM iris.unitary_electoral_division;
    """
    )
    """ Create geo index for uk_ward"""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS uk_ward__geometry_geom_idx
            ON iris.uk_ward USING gist
            (geometry)
            TABLESPACE pg_default;
    """
    )
    
    
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_ward_epc_data
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
            LEFT JOIN iris.uk_ward b
            ON ST_Intersects(b.geometry, a.point)
            GROUP BY b.name, b.geometry 
        WITH NO DATA;
    """
    )
    
    """ Create materialized view containing GeoJSON."""
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.uk_ward_epc
            AS
            SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(jsonb_build_object('type', 'Feature', 'geometry', st_asgeojson(ST_SIMPLIFY(geometry, 0.0001))::json, 'properties', to_jsonb(t.*) - 'geometry'::text))) AS geojson
            FROM iris.uk_ward_epc_data t
            WITH NO DATA;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.uk_ward_epc;
    """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.uk_ward_shape_geom_idx;
    """
    )

    op.execute(
        """
        DROP TABLE IF EXISTS iris.uk_ward;
    """
    )
    op.execute(
        """
        DROP TABLE IF EXISTS iris.district_borough_unitary_ward;
    """
    )
    op.execute(
        """
        DROP TABLE IF EXISTS iris.unitary_electoral_division;
    """
    )
    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.uk_ward_objectid_seq;
    """
    )
    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.district_borough_unitary_ward_fid_seq1;
    """
    )
    op.execute(
        """
        DROP SEQUENCE IF EXISTS iris.unitary_electoral_division_fid_seq1;
    """
    )
