# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""update_buildings_epc_is_residential

Revision ID: 473ce669077d
Revises: 0e6126841f0c
Create Date: 2025-09-17 13:54:24.519128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '473ce669077d'
down_revision: Union[str, None] = '0e6126841f0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEPENDENT_MATERIALIZED_VIEWS = [
    "iris.uk_ward_epc",
    "iris.uk_ward_epc_data",
    "iris.uk_region_epc",
    "iris.uk_region_epc_data",
    "iris.district_borough_unitary_epc",
    "iris.district_borough_unitary_epc_data",
    "iris.boundary_line_ceremonial_counties_epc",
    "iris.boundary_line_ceremonial_counties_epc_data",
]

DATA_MATERIALIZED_VIEWS = [
    "iris.uk_ward_epc_data",
    "iris.uk_region_epc_data",
    "iris.district_borough_unitary_epc_data",
    "iris.boundary_line_ceremonial_counties_epc_data",
]

GEOJSON_MATERIALIZED_VIEWS = [
    "iris.uk_ward_epc",
    "iris.uk_region_epc",
    "iris.district_borough_unitary_epc",
    "iris.boundary_line_ceremonial_counties_epc",
]


def upgrade() -> None:
    """Upgrade schema."""

    for mv in DEPENDENT_MATERIALIZED_VIEWS:
        op.execute(sa.text(f"DROP MATERIALIZED VIEW IF EXISTS {mv};"))

    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS iris.building_epc;"))

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.building_epc AS
        SELECT a.uprn,
               b.epc_rating,
               a.point
        FROM iris.building a
        LEFT JOIN iris.epc_assessment b
          ON a.uprn = b.uprn
        WHERE a.is_residential IS TRUE;
        """
    )

    op.execute(
        """
        CREATE INDEX idx_building_epc_geom
            ON iris.building_epc
            USING GIST (point);
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_ward_epc_data
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

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_region_epc_data
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

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.district_borough_unitary_epc_data
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
            LEFT JOIN iris.district_borough_unitary b
              ON ST_Intersects(b.geometry, a.point)
            GROUP BY b.name, b.geometry
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.boundary_line_ceremonial_counties_epc_data
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
            LEFT JOIN iris.boundary_line_ceremonial_counties b
              ON ST_Intersects(b.geometry, a.point)
            GROUP BY b.name, b.geometry
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_ward_epc
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
            FROM iris.uk_ward_epc_data t
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_region_epc
            TABLESPACE pg_default
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
            FROM iris.uk_region_epc_data t
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.district_borough_unitary_epc
            TABLESPACE pg_default
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
            FROM iris.district_borough_unitary_epc_data t
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.boundary_line_ceremonial_counties_epc
            TABLESPACE pg_default
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
            FROM iris.boundary_line_ceremonial_counties_epc_data t
        WITH NO DATA;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    for mv in DEPENDENT_MATERIALIZED_VIEWS:
        op.execute(sa.text(f"DROP MATERIALIZED VIEW IF EXISTS {mv};"))

    op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS iris.building_epc;"))

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.building_epc AS
        SELECT a.uprn,
               b.epc_rating,
               a.point
        FROM iris.building a
        LEFT JOIN iris.epc_assessment b
          ON a.uprn = b.uprn
        """
    )

    op.execute(
        """
        CREATE INDEX idx_building_epc_geom
            ON iris.building_epc
            USING GIST (point);
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_ward_epc_data
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

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_region_epc_data
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

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.district_borough_unitary_epc_data
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
            LEFT JOIN iris.district_borough_unitary b
              ON ST_Intersects(b.geometry, a.point)
            GROUP BY b.name, b.geometry
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.boundary_line_ceremonial_counties_epc_data
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
            LEFT JOIN iris.boundary_line_ceremonial_counties b
              ON ST_Intersects(b.geometry, a.point)
            GROUP BY b.name, b.geometry
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_ward_epc
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
            FROM iris.uk_ward_epc_data t
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.uk_region_epc
            TABLESPACE pg_default
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
            FROM iris.uk_region_epc_data t
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.district_borough_unitary_epc
            TABLESPACE pg_default
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
            FROM iris.district_borough_unitary_epc_data t
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.boundary_line_ceremonial_counties_epc
            TABLESPACE pg_default
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
            FROM iris.boundary_line_ceremonial_counties_epc_data t
        WITH NO DATA;
        """
    )
