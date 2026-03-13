# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""039_create_deprivation_lookup_tables_and_mv

Revision ID: f4b7c2d9a1e3
Revises: d19f556331db
Create Date: 2026-02-17 16:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f4b7c2d9a1e3"
down_revision: Union[str, None] = "d19f556331db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS iris.msoa_boundaries_id_seq
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
        """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS iris.msoa_boundaries
        (
            id integer NOT NULL DEFAULT nextval('iris.msoa_boundaries_id_seq'::regclass),
            msoa21cd character varying(9) COLLATE pg_catalog."default",
            msoa21nm character varying(39) COLLATE pg_catalog."default",
            msoa21nmw character varying(29) COLLATE pg_catalog."default",
            bng_e numeric(10,0),
            bng_n numeric(10,0),
            lat double precision,
            "long" double precision,
            globalid character varying(38) COLLATE pg_catalog."default",
            geom geometry(MultiPolygon,27700),
            CONSTRAINT msoa_boundaries_pkey PRIMARY KEY (id)
        )
        TABLESPACE pg_default;
        """)

    op.execute("""
        ALTER SEQUENCE IF EXISTS iris.msoa_boundaries_id_seq
            OWNED BY iris.msoa_boundaries.id;
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS msoa_boundaries_geom_geom_idx
            ON iris.msoa_boundaries USING gist
            (geom)
            WITH (fillfactor=90, buffering=auto)
            TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS iris.oa_boundaries_analytics_id_seq
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;
        """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS iris.oa_boundaries_analytics
        (
            id integer NOT NULL DEFAULT nextval('iris.oa_boundaries_analytics_id_seq'::regclass),
            oa21cd character varying(9) COLLATE pg_catalog."default",
            lsoa21cd character varying(9) COLLATE pg_catalog."default",
            lsoa21nm character varying(40) COLLATE pg_catalog."default",
            lsoa21nmw character varying(29) COLLATE pg_catalog."default",
            bng_e numeric(10,0),
            bng_n numeric(10,0),
            lat double precision,
            "long" double precision,
            globalid character varying(38) COLLATE pg_catalog."default",
            geom geometry(MultiPolygon,27700),
            CONSTRAINT oa_boundaries_analytics_pkey PRIMARY KEY (id)
        )
        TABLESPACE pg_default;
        """)

    op.execute("""
        ALTER SEQUENCE IF EXISTS iris.oa_boundaries_analytics_id_seq
            OWNED BY iris.oa_boundaries_analytics.id;
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_oa_geom_gist
            ON iris.oa_boundaries_analytics USING gist
            (geom)
            WITH (fillfactor=90, buffering=auto)
            TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS oa_boundaries_analytics_geom_geom_idx
            ON iris.oa_boundaries_analytics USING gist
            (geom)
            WITH (fillfactor=90, buffering=auto)
            TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS iris.ons_deprivation_metrics
        (
            mlsoa_id text COLLATE pg_catalog."default",
            dep_not_apply integer,
            dep_0 integer,
            dep_1 integer,
            dep_2 integer,
            dep_3 integer,
            dep_4 integer
        )
        TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS iris.ons_deprivation_metrics_analytics
        (
            oa_id text COLLATE pg_catalog."default",
            dep_not_apply integer,
            dep_0 integer,
            dep_1 integer,
            dep_2 integer,
            dep_3 integer,
            dep_4 integer
        )
        TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.msoa_deprivation_data
        TABLESPACE pg_default
        AS
        SELECT m.mlsoa_id,
            b.msoa21nm AS area_nm,
            m.dep_not_apply,
            m.dep_0,
            m.dep_1,
            m.dep_2,
            m.dep_3,
            m.dep_4,
            m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4 AS dep_total,
                CASE
                    WHEN (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4) > 0 THEN m.dep_0::numeric * 100.0 / (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4)::numeric
                    ELSE NULL::numeric
                END AS dep_pct_0,
                CASE
                    WHEN (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4) > 0 THEN m.dep_1::numeric * 100.0 / (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4)::numeric
                    ELSE NULL::numeric
                END AS dep_pct_1,
                CASE
                    WHEN (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4) > 0 THEN m.dep_2::numeric * 100.0 / (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4)::numeric
                    ELSE NULL::numeric
                END AS dep_pct_2,
                CASE
                    WHEN (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4) > 0 THEN m.dep_3::numeric * 100.0 / (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4)::numeric
                    ELSE NULL::numeric
                END AS dep_pct_3,
                CASE
                    WHEN (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4) > 0 THEN m.dep_4::numeric * 100.0 / (m.dep_0 + m.dep_1 + m.dep_2 + m.dep_3 + m.dep_4)::numeric
                    ELSE NULL::numeric
                END AS dep_pct_4,
            b.geom
        FROM iris.ons_deprivation_metrics m
            JOIN iris.msoa_boundaries b ON m.mlsoa_id = b.msoa21cd::text
        WITH DATA;
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS msoa_deprivation_data_geom_gix
            ON iris.msoa_deprivation_data USING gist
            (geom)
            TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS msoa_deprivation_data_pk
            ON iris.msoa_deprivation_data USING btree
            (mlsoa_id COLLATE pg_catalog."default")
            TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.msoa_deprivation_geojson
        TABLESPACE pg_default
        AS
        WITH base AS (
                SELECT t.mlsoa_id,
                    t.area_nm,
                    t.dep_not_apply,
                    t.dep_0,
                    t.dep_1,
                    t.dep_2,
                    t.dep_3,
                    t.dep_4,
                    t.dep_total,
                    t.dep_pct_0,
                    t.dep_pct_1,
                    t.dep_pct_2,
                    t.dep_pct_3,
                    t.dep_pct_4,
                    st_setsrid(t.geom, 27700) AS geom_27700
                FROM iris.msoa_deprivation_data t
                ), cov AS (
                SELECT base.mlsoa_id,
                    base.area_nm,
                    base.dep_not_apply,
                    base.dep_0,
                    base.dep_1,
                    base.dep_2,
                    base.dep_3,
                    base.dep_4,
                    base.dep_total,
                    base.dep_pct_0,
                    base.dep_pct_1,
                    base.dep_pct_2,
                    base.dep_pct_3,
                    base.dep_pct_4,
                    base.geom_27700,
                    st_coveragesimplify(base.geom_27700, 50::double precision) OVER () AS geom_simpl
                FROM base
                )
        SELECT json_build_object('type', 'FeatureCollection', 'features', json_agg(json_build_object('type', 'Feature', 'geometry', st_asgeojson(st_transform(st_setsrid(geom_simpl, 27700), 4326), 5)::json, 'properties', (to_jsonb(cov.*) - 'geom_27700'::text - 'geom_simpl'::text)::json))) AS geojson
        FROM cov
        WITH DATA;
        """)

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.oa_area_membership_mv
        TABLESPACE pg_default
        AS
        WITH oa AS (
                SELECT oa_boundaries_analytics.oa21cd,
                    st_transform(oa_boundaries_analytics.geom, 4326) AS geom_4326
                FROM iris.oa_boundaries_analytics
                )
        SELECT DISTINCT oa.oa21cd,
            v.area_level,
            v.area_name
        FROM oa
            JOIN iris.building_epc_analytics bea ON oa.geom_4326 && bea.point AND st_contains(oa.geom_4326, bea.point)
            CROSS JOIN LATERAL ( VALUES ('region'::text,bea.region_name), ('county'::text,bea.county_name), ('district'::text,bea.district_name), ('ward'::text,bea.ward_name)) v(area_level, area_name)
        WHERE v.area_name IS NOT NULL
        WITH NO DATA;
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_oa_area_membership_mv_lookup
            ON iris.oa_area_membership_mv USING btree
            (area_level COLLATE pg_catalog."default", area_name COLLATE pg_catalog."default", oa21cd COLLATE pg_catalog."default")
            TABLESPACE pg_default;
        """)

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_oa_area_membership_mv_uq
            ON iris.oa_area_membership_mv USING btree
            (oa21cd COLLATE pg_catalog."default", area_level COLLATE pg_catalog."default", area_name COLLATE pg_catalog."default")
            TABLESPACE pg_default;
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP INDEX IF EXISTS iris.idx_oa_area_membership_mv_lookup;
        """)
    op.execute("""
        DROP INDEX IF EXISTS iris.idx_oa_area_membership_mv_uq;
        """)
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.oa_area_membership_mv;
        """)
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.msoa_deprivation_geojson;
        """)
    op.execute("""
        DROP INDEX IF EXISTS iris.msoa_deprivation_data_geom_gix;
        """)
    op.execute("""
        DROP INDEX IF EXISTS iris.msoa_deprivation_data_pk;
        """)
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.msoa_deprivation_data;
        """)
    op.execute("""
        DROP TABLE IF EXISTS iris.ons_deprivation_metrics_analytics;
        """)
    op.execute("""
        DROP TABLE IF EXISTS iris.ons_deprivation_metrics;
        """)
    op.execute("""
        DROP INDEX IF EXISTS iris.idx_oa_geom_gist;
        """)
    op.execute("""
        DROP INDEX IF EXISTS iris.oa_boundaries_analytics_geom_geom_idx;
        """)
    op.execute("""
        DROP TABLE IF EXISTS iris.oa_boundaries_analytics;
        """)
    op.execute("""
        DROP SEQUENCE IF EXISTS iris.oa_boundaries_analytics_id_seq;
        """)
    op.execute("""
        DROP INDEX IF EXISTS iris.msoa_boundaries_geom_geom_idx;
        """)
    op.execute("""
        DROP TABLE IF EXISTS iris.msoa_boundaries;
        """)
    op.execute("""
        DROP SEQUENCE IF EXISTS iris.msoa_boundaries_id_seq;
        """)
