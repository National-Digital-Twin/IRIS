# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""030_recreate_building_epc_analytics_with_active_snapshot_dates

Revision ID: 5d3b574055a5
Revises: 9e07a98054cc
Create Date: 2025-11-06 12:32:51.655070

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5d3b574055a5'
down_revision: Union[str, None] = '9e07a98054cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_indices():
    """Create all indexes on building_epc_analytics (from migrations 024, 025, and new timeline indexes)."""

    # From migration 024 - basic indexes
    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_uprn_idx
        ON iris.building_epc_analytics(uprn);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_point_idx
        ON iris.building_epc_analytics USING GIST(point);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_name_idx
        ON iris.building_epc_analytics(region_name);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_lodgement_date_idx
        ON iris.building_epc_analytics(lodgement_date);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_county_name_idx
        ON iris.building_epc_analytics(county_name);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_district_name_idx
        ON iris.building_epc_analytics(district_name);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_ward_name_idx
        ON iris.building_epc_analytics(ward_name);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_epc_active_idx
        ON iris.building_epc_analytics(epc_active);
    """)

    # From migration 025 - partial indexes for active EPC charts
    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_fuel_types_idx
        ON iris.building_epc_analytics (type, fuel_type)
        WHERE epc_active = true
            AND type IS NOT NULL
            AND fuel_type IS NOT NULL;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_epc_ratings_idx
        ON iris.building_epc_analytics (epc_rating, region_name)
        WHERE epc_active = true;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_attributes_idx
        ON iris.building_epc_analytics (
            region_name,
            has_roof_solar_panels,
            window_glazing,
            floor_construction,
            roof_insulation_thickness,
            roof_construction,
            wall_construction
        )
        WHERE epc_active = true;
    """)

    # New indexes for timeline charts (historical data via active_snapshots)
    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_epc_rating_idx
        ON iris.building_epc_analytics(epc_rating);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_type_idx
        ON iris.building_epc_analytics(type);
    """)


def upgrade() -> None:
    """Recreate building_epc_analytics with active_snapshots column."""

    # Drop existing materialized view
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics CASCADE;
    """)

    # Recreate with active_snapshots column
    op.execute("""
        CREATE MATERIALIZED VIEW iris.building_epc_analytics AS (
            WITH active_epcs AS (
                -- Find the most recent valid EPC per UPRN (for epc_active flag)
                SELECT DISTINCT ON (uprn) *
                FROM iris.epc_assessment
                WHERE lodgement_date IS NOT NULL AND expiry_date >= CURRENT_DATE
                ORDER BY uprn, lodgement_date DESC
            ),
            year_end_dates AS (
                -- Generate all year-end dates from earliest to current year
                SELECT generate_series(
                    DATE_TRUNC('year', (SELECT MIN(lodgement_date) FROM iris.epc_assessment WHERE lodgement_date IS NOT NULL))::date + interval '1 year' - interval '1 day',
                    DATE_TRUNC('year', CURRENT_DATE)::date + interval '1 year' - interval '1 day',
                    interval '1 year'
                )::date as snapshot_date
            ),
            snapshot_lookup AS (
                -- For each EPC, find year-end dates where it was the active EPC (most recent valid one)
                WITH epc_snapshots AS (
                    SELECT
                        ea.uprn,
                        ea.lodgement_date,
                        yed.snapshot_date,
                        ROW_NUMBER() OVER (
                            PARTITION BY ea.uprn, yed.snapshot_date
                            ORDER BY ea.lodgement_date DESC
                        ) as rn
                    FROM iris.epc_assessment ea
                    CROSS JOIN year_end_dates yed
                    WHERE ea.lodgement_date <= yed.snapshot_date
                      AND ea.expiry_date >= yed.snapshot_date
                      AND ea.lodgement_date IS NOT NULL
                      AND ea.expiry_date IS NOT NULL
                )
                SELECT
                    uprn,
                    lodgement_date,
                    ARRAY_AGG(snapshot_date ORDER BY snapshot_date) as active_snapshots
                FROM epc_snapshots
                WHERE rn = 1  -- Only the most recent EPC at each snapshot
                GROUP BY uprn, lodgement_date
            )
            SELECT
                b.uprn,
                b.point,
                b.is_residential,
                ea.lodgement_date,
                ea.epc_rating,
                ea.sap_rating,
                ea.expiry_date,
                COALESCE(su_epc.type, su_build.type) AS type,
                COALESCE(su_epc.built_form, su_build.built_form) AS built_form,
                COALESCE(su_epc.fuel_type, su_build.fuel_type) AS fuel_type,
                COALESCE(su_epc.window_glazing, su_build.window_glazing) AS window_glazing,
                COALESCE(su_epc.wall_construction, su_build.wall_construction) AS wall_construction,
                COALESCE(su_epc.wall_insulation, su_build.wall_insulation) AS wall_insulation,
                COALESCE(su_epc.roof_construction, su_build.roof_construction) AS roof_construction,
                COALESCE(su_epc.roof_insulation, su_build.roof_insulation) AS roof_insulation,
                COALESCE(su_epc.roof_insulation_thickness, su_build.roof_insulation_thickness) AS roof_insulation_thickness,
                COALESCE(su_epc.floor_construction, su_build.floor_construction) AS floor_construction,
                COALESCE(su_epc.floor_insulation, su_build.floor_insulation) AS floor_insulation,
                COALESCE(su_epc.has_roof_solar_panels, su_build.has_roof_solar_panels) AS has_roof_solar_panels,
                COALESCE(su_epc.roof_material, su_build.roof_material) AS roof_material,
                COALESCE(su_epc.roof_aspect_area_facing_north_m2, su_build.roof_aspect_area_facing_north_m2) AS roof_aspect_area_facing_north_m2,
                COALESCE(su_epc.roof_aspect_area_facing_east_m2, su_build.roof_aspect_area_facing_east_m2) AS roof_aspect_area_facing_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_m2, su_build.roof_aspect_area_facing_south_m2) AS roof_aspect_area_facing_south_m2,
                COALESCE(su_epc.roof_aspect_area_facing_west_m2, su_build.roof_aspect_area_facing_west_m2) AS roof_aspect_area_facing_west_m2,
                COALESCE(su_epc.roof_aspect_area_facing_north_east_m2, su_build.roof_aspect_area_facing_north_east_m2) AS roof_aspect_area_facing_north_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_east_m2, su_build.roof_aspect_area_facing_south_east_m2) AS roof_aspect_area_facing_south_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_west_m2, su_build.roof_aspect_area_facing_south_west_m2) AS roof_aspect_area_facing_south_west_m2,
                COALESCE(su_epc.roof_aspect_area_facing_north_west_m2, su_build.roof_aspect_area_facing_north_west_m2) AS roof_aspect_area_facing_north_west_m2,
                COALESCE(su_epc.roof_aspect_area_indeterminable_m2, su_build.roof_aspect_area_indeterminable_m2) AS roof_aspect_area_indeterminable_m2,
                COALESCE(su_epc.roof_shape, su_build.roof_shape) AS roof_shape,
                COALESCE(er.name, sawr.name) AS region_name,
                blcc.name AS county_name,
                dbu.name AS district_name,
                COALESCE(dbuw.name, ued.name) AS ward_name,
                CASE
                    WHEN aes.id IS NOT NULL THEN true
                    ELSE false
                END AS epc_active,
                sl.active_snapshots
            FROM iris.building b
            LEFT JOIN iris.epc_assessment ea ON ea.uprn = b.uprn
            LEFT JOIN active_epcs aes ON ea.id = aes.id
            LEFT JOIN snapshot_lookup sl ON sl.uprn = b.uprn AND sl.lodgement_date = ea.lodgement_date
            LEFT JOIN iris.structure_unit su_epc ON su_epc.epc_assessment_id = ea.id
            LEFT JOIN iris.structure_unit su_build
                ON su_build.uprn = b.uprn
                AND su_build.epc_assessment_id IS NULL
                AND ea.id IS NULL
            JOIN iris.boundary_line_ceremonial_counties blcc ON ST_INTERSECTS(blcc.geometry, b.point)
            JOIN iris.district_borough_unitary dbu ON ST_INTERSECTS(dbu.geometry, b.point)
            LEFT JOIN iris.district_borough_unitary_ward dbuw ON ST_INTERSECTS(dbuw.geometry, b.point)
            LEFT JOIN iris.unitary_electoral_division ued ON ST_INTERSECTS(ued.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        )
        WITH NO DATA;
    """)

    # Create all indexes
    _create_indices()

    # Drop building_epc_active_by_year as it's no longer needed
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_active_by_year CASCADE;
    """)


def downgrade() -> None:
    """Revert to previous building_epc_analytics definition without active_snapshots."""

    # Drop current view
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics CASCADE;
    """)

    # Recreate previous definition (from migration 024, without active_snapshots)
    op.execute("""
        CREATE MATERIALIZED VIEW iris.building_epc_analytics AS (
            WITH active_epcs AS (
                SELECT DISTINCT ON (uprn) *
                FROM iris.epc_assessment
                WHERE lodgement_date IS NOT NULL AND expiry_date >= CURRENT_DATE
                ORDER BY uprn, lodgement_date DESC
            )
            SELECT
                b.uprn,
                b.point,
                b.is_residential,
                ea.lodgement_date,
                ea.epc_rating,
                ea.sap_rating,
                ea.expiry_date,
                COALESCE(su_epc.type, su_build.type) AS type,
                COALESCE(su_epc.built_form, su_build.built_form) AS built_form,
                COALESCE(su_epc.fuel_type, su_build.fuel_type) AS fuel_type,
                COALESCE(su_epc.window_glazing, su_build.window_glazing) AS window_glazing,
                COALESCE(su_epc.wall_construction, su_build.wall_construction) AS wall_construction,
                COALESCE(su_epc.wall_insulation, su_build.wall_insulation) AS wall_insulation,
                COALESCE(su_epc.roof_construction, su_build.roof_construction) AS roof_construction,
                COALESCE(su_epc.roof_insulation, su_build.roof_insulation) AS roof_insulation,
                COALESCE(su_epc.roof_insulation_thickness, su_build.roof_insulation_thickness) AS roof_insulation_thickness,
                COALESCE(su_epc.floor_construction, su_build.floor_construction) AS floor_construction,
                COALESCE(su_epc.floor_insulation, su_build.floor_insulation) AS floor_insulation,
                COALESCE(su_epc.has_roof_solar_panels, su_build.has_roof_solar_panels) AS has_roof_solar_panels,
                COALESCE(su_epc.roof_material, su_build.roof_material) AS roof_material,
                COALESCE(su_epc.roof_aspect_area_facing_north_m2, su_build.roof_aspect_area_facing_north_m2) AS roof_aspect_area_facing_north_m2,
                COALESCE(su_epc.roof_aspect_area_facing_east_m2, su_build.roof_aspect_area_facing_east_m2) AS roof_aspect_area_facing_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_m2, su_build.roof_aspect_area_facing_south_m2) AS roof_aspect_area_facing_south_m2,
                COALESCE(su_epc.roof_aspect_area_facing_west_m2, su_build.roof_aspect_area_facing_west_m2) AS roof_aspect_area_facing_west_m2,
                COALESCE(su_epc.roof_aspect_area_facing_north_east_m2, su_build.roof_aspect_area_facing_north_east_m2) AS roof_aspect_area_facing_north_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_east_m2, su_build.roof_aspect_area_facing_south_east_m2) AS roof_aspect_area_facing_south_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_west_m2, su_build.roof_aspect_area_facing_south_west_m2) AS roof_aspect_area_facing_south_west_m2,
                COALESCE(su_epc.roof_aspect_area_facing_north_west_m2, su_build.roof_aspect_area_facing_north_west_m2) AS roof_aspect_area_facing_north_west_m2,
                COALESCE(su_epc.roof_aspect_area_indeterminable_m2, su_build.roof_aspect_area_indeterminable_m2) AS roof_aspect_area_indeterminable_m2,
                COALESCE(su_epc.roof_shape, su_build.roof_shape) AS roof_shape,
                COALESCE(er.name, sawr.name) AS region_name,
                blcc.name AS county_name,
                dbu.name AS district_name,
                COALESCE(dbuw.name, ued.name) AS ward_name,
                CASE
                    WHEN aes.id IS NOT NULL THEN true
                    ELSE false
                END AS epc_active
            FROM iris.building b
            LEFT JOIN iris.epc_assessment ea ON ea.uprn = b.uprn
            LEFT JOIN active_epcs aes ON ea.id = aes.id
            LEFT JOIN iris.structure_unit su_epc ON su_epc.epc_assessment_id = ea.id
            LEFT JOIN iris.structure_unit su_build
                ON su_build.uprn = b.uprn
                AND su_build.epc_assessment_id IS NULL
                AND ea.id IS NULL
            JOIN iris.boundary_line_ceremonial_counties blcc ON ST_INTERSECTS(blcc.geometry, b.point)
            JOIN iris.district_borough_unitary dbu ON ST_INTERSECTS(dbu.geometry, b.point)
            LEFT JOIN iris.district_borough_unitary_ward dbuw ON ST_INTERSECTS(dbuw.geometry, b.point)
            LEFT JOIN iris.unitary_electoral_division ued ON ST_INTERSECTS(ued.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        )
        WITH NO DATA;
    """)

    # Recreate indexes
    _create_indices()

    # Recreate building_epc_active_by_year
    op.execute("""
        CREATE MATERIALIZED VIEW iris.building_epc_active_by_year AS
        WITH RECURSIVE date_range AS (
            SELECT
                (DATE_TRUNC('year', MIN(lodgement_date))::date + interval '1 year' - interval '1 day')::date as snapshot_date,
                (DATE_TRUNC('year', CURRENT_DATE)::date + interval '1 year' - interval '1 day')::date as max_date
            FROM iris.building_epc_analytics
            WHERE lodgement_date IS NOT NULL

            UNION ALL

            SELECT
                (snapshot_date + interval '1 year')::date,
                max_date
            FROM date_range
            WHERE snapshot_date < max_date
        ),
        snapshots AS (
            SELECT snapshot_date FROM date_range WHERE snapshot_date IS NOT NULL
        ),
        snapshot_per_year AS (
            SELECT
                s.snapshot_date,
                b.uprn,
                b.lodgement_date,
                ROW_NUMBER() OVER (
                    PARTITION BY s.snapshot_date, b.uprn
                    ORDER BY b.lodgement_date DESC
                ) as rn
            FROM snapshots s
            INNER JOIN iris.building_epc_analytics b
                ON b.lodgement_date <= s.snapshot_date
                AND b.expiry_date >= s.snapshot_date
            WHERE b.lodgement_date IS NOT NULL
              AND b.expiry_date IS NOT NULL
              AND b.sap_rating IS NOT NULL
        )
        SELECT
            snapshot_date,
            uprn,
            lodgement_date
        FROM snapshot_per_year
        WHERE rn = 1
        WITH NO DATA;
    """)

    op.execute("""
        CREATE INDEX building_epc_active_by_year_snapshot_date_idx
        ON iris.building_epc_active_by_year(snapshot_date);
    """)

    op.execute("""
        CREATE INDEX building_epc_active_by_year_epc_ref_idx
        ON iris.building_epc_active_by_year(uprn, lodgement_date);
    """)

    op.execute("""
        CREATE INDEX building_epc_analytics_uprn_lodgement_idx
        ON iris.building_epc_analytics(uprn, lodgement_date);
    """)
