# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""035_recreate_building_epc_analytics

Revision ID: 44de9a59d873
Revises: 5c66700e5c72
Create Date: 2026-01-06 16:07:40.889098

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44de9a59d873"
down_revision: Union[str, None] = "5c66700e5c72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_indices():
    """Create all indexes on building_epc_analytics (from migrations
    - 024
    - 025
    - new timeline indexes mentioned in 030
    - 033
    - 034)."""

    # From migration 024 - basic indexes
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_uprn_idx
        ON iris.building_epc_analytics(uprn);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_point_idx
        ON iris.building_epc_analytics USING GIST(point);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_name_idx
        ON iris.building_epc_analytics(region_name);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_lodgement_date_idx
        ON iris.building_epc_analytics(lodgement_date);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_county_name_idx
        ON iris.building_epc_analytics(county_name);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_district_name_idx
        ON iris.building_epc_analytics(district_name);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_ward_name_idx
        ON iris.building_epc_analytics(ward_name);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_epc_active_idx
        ON iris.building_epc_analytics(epc_active);
    """
    )

    # From migration 025 - partial indexes for active EPC charts
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_fuel_types_idx
        ON iris.building_epc_analytics (type, fuel_type)
        WHERE epc_active = true
            AND type IS NOT NULL
            AND fuel_type IS NOT NULL;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_epc_ratings_idx
        ON iris.building_epc_analytics (epc_rating, region_name)
        WHERE epc_active = true;
    """
    )

    op.execute(
        """
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
    """
    )

    # New indexes for timeline charts (historical data via active_snapshots)
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_epc_rating_idx
        ON iris.building_epc_analytics(epc_rating);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_type_idx
        ON iris.building_epc_analytics(type);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_point_active_idx
        ON iris.building_epc_analytics USING GIST(point)
        WHERE epc_active = true;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_name_active_idx
        ON iris.building_epc_analytics (region_name)
        WHERE epc_active = true;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_county_name_active_idx
        ON iris.building_epc_analytics (county_name)
        WHERE epc_active = true;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_district_name_active_idx
        ON iris.building_epc_analytics (district_name)
        WHERE epc_active = true;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_ward_name_active_idx
        ON iris.building_epc_analytics (ward_name)
        WHERE epc_active = true;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_fuel_types_idx
        ON iris.building_epc_analytics (region_name, type, fuel_type)
        WHERE epc_active = true AND type IS NOT NULL AND fuel_type IS NOT NULL;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_county_fuel_types_idx
        ON iris.building_epc_analytics (county_name, type, fuel_type)
        WHERE epc_active = true AND type IS NOT NULL AND fuel_type IS NOT NULL;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_district_fuel_types_idx
        ON iris.building_epc_analytics (district_name, type, fuel_type)
        WHERE epc_active = true AND type IS NOT NULL AND fuel_type IS NOT NULL;
    """
    )


def _create_building_epc_analytics_aggregates_view():
    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.building_epc_analytics_aggregates AS
        WITH snapshot_dates AS (
            SELECT generate_series(
                DATE_TRUNC('year', (SELECT MIN(lodgement_date) FROM iris.building_epc_analytics WHERE lodgement_date IS NOT NULL))::date + interval '1 year' - interval '1 day',
                DATE_TRUNC('year', CURRENT_DATE)::date + interval '1 year' - interval '1 day',
                interval '1 year'
            )::date as snapshot_date
        ),
        issued_counts AS (
            SELECT
                sd.snapshot_date,
                bea.region_name,
                bea.county_name,
                bea.district_name,
                bea.ward_name,
                bea.type,
                COUNT(DISTINCT bea.uprn) as total_issued_count
            FROM snapshot_dates sd
            CROSS JOIN iris.building_epc_analytics bea
            WHERE bea.lodgement_date <= sd.snapshot_date
              AND bea.active_snapshots IS NOT NULL
            GROUP BY sd.snapshot_date, bea.region_name, bea.county_name, bea.district_name, bea.ward_name, bea.type
        ),
        active_aggregates AS (
            SELECT
                unnest(active_snapshots) as snapshot_date,
                region_name,
                county_name,
                district_name,
                ward_name,
                type,
                COUNT(*) as active_epc_count,
                SUM(sap_rating) as sum_sap_rating,
                COUNT(*) FILTER (WHERE epc_rating = 'A') as count_rating_a,
                COUNT(*) FILTER (WHERE epc_rating = 'B') as count_rating_b,
                COUNT(*) FILTER (WHERE epc_rating = 'C') as count_rating_c,
                COUNT(*) FILTER (WHERE epc_rating = 'D') as count_rating_d,
                COUNT(*) FILTER (WHERE epc_rating = 'E') as count_rating_e,
                COUNT(*) FILTER (WHERE epc_rating = 'F') as count_rating_f,
                COUNT(*) FILTER (WHERE epc_rating = 'G') as count_rating_g
            FROM iris.building_epc_analytics
            WHERE active_snapshots IS NOT NULL
            GROUP BY snapshot_date, region_name, county_name, district_name, ward_name, type
        )
        SELECT
            aa.snapshot_date,
            aa.region_name,
            aa.county_name,
            aa.district_name,
            aa.ward_name,
            aa.type,
            aa.active_epc_count,
            aa.sum_sap_rating,
            aa.count_rating_a,
            aa.count_rating_b,
            aa.count_rating_c,
            aa.count_rating_d,
            aa.count_rating_e,
            aa.count_rating_f,
            aa.count_rating_g,
            (ic.total_issued_count - aa.active_epc_count) as expired_epc_count
        FROM active_aggregates aa
        JOIN issued_counts ic
            ON aa.snapshot_date = ic.snapshot_date
            AND aa.region_name IS NOT DISTINCT FROM ic.region_name
            AND aa.county_name IS NOT DISTINCT FROM ic.county_name
            AND aa.district_name IS NOT DISTINCT FROM ic.district_name
            AND aa.ward_name IS NOT DISTINCT FROM ic.ward_name
            AND aa.type IS NOT DISTINCT FROM ic.type
        WITH NO DATA;
    """
    )

    op.execute(
        """
        CREATE INDEX building_epc_analytics_aggregates_snapshot_date_idx
        ON iris.building_epc_analytics_aggregates(snapshot_date);
    """
    )

    op.execute(
        """
        CREATE INDEX building_epc_analytics_aggregates_region_snapshot_idx
        ON iris.building_epc_analytics_aggregates(region_name, snapshot_date);
    """
    )

    op.execute(
        """
        CREATE INDEX building_epc_analytics_aggregates_county_snapshot_idx
        ON iris.building_epc_analytics_aggregates(county_name, snapshot_date);
    """
    )

    op.execute(
        """
        CREATE INDEX building_epc_analytics_aggregates_district_snapshot_idx
        ON iris.building_epc_analytics_aggregates(district_name, snapshot_date);
    """
    )

    op.execute(
        """
        CREATE INDEX building_epc_analytics_aggregates_ward_snapshot_idx
        ON iris.building_epc_analytics_aggregates(ward_name, snapshot_date);
    """
    )

    op.execute(
        """
        CREATE INDEX building_epc_analytics_aggregates_snapshot_type_idx
        ON iris.building_epc_analytics_aggregates(snapshot_date, type);
    """
    )


def _create_building_extreme_weather_analytics_view():
    op.execute(
        """
        CREATE MATERIALIZED VIEW iris.building_extreme_weather_analytics AS (
            WITH buildings_affected_by_icing_days AS (
                SELECT uprn, true AS affected
                FROM iris.building_weather_analytics
                WHERE icing_days > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY icing_days
                    )
                    FROM iris.building_weather_analytics
                )
            ),
            buildings_affected_by_hsds AS (
                SELECT uprn, true AS affected
                FROM iris.building_weather_analytics
                WHERE hsd_40_median > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY hsd_40_median
                    )
                    FROM iris.building_weather_analytics
                )
            ),
            buildings_affected_by_wdrp AS (
                SELECT uprn, true AS affected
                FROM iris.building_weather_analytics
                WHERE wdr_40_median_0 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_0
                    )
                    FROM iris.building_weather_analytics
                )
                OR wdr_40_median_45 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_45
                    )
                    FROM iris.building_weather_analytics
                )
                OR wdr_40_median_90 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_90
                    )
                    FROM iris.building_weather_analytics
                )
                OR wdr_40_median_135 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_135
                    )
                    FROM iris.building_weather_analytics
                )
                OR wdr_40_median_180 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_180
                    )
                    FROM iris.building_weather_analytics
                )
                OR wdr_40_median_225 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_225
                    )
                    FROM iris.building_weather_analytics
                )
                OR wdr_40_median_270 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_270
                    )
                    FROM iris.building_weather_analytics
                )
                OR wdr_40_median_315 > (
                    SELECT percentile_cont(0.75) WITHIN GROUP (
                        ORDER BY wdr_40_median_315
                    )
                    FROM iris.building_weather_analytics
                )
            )
            SELECT DISTINCT ON (bwa.uprn)
                bwa.uprn,
                bwa.point,
                babi.affected as affected_by_icing_days,
                babh.affected as affected_by_hsds,
                babw.affected as affected_by_wdr,
                bea.region_name,
                bea.county_name,
                bea.district_name,
                bea.ward_name
            FROM iris.building_weather_analytics bwa
            LEFT JOIN buildings_affected_by_icing_days babi ON bwa.uprn = babi.uprn
            LEFT JOIN buildings_affected_by_hsds babh ON bwa.uprn = babh.uprn
            LEFT JOIN buildings_affected_by_wdrp babw ON bwa.uprn = babw.uprn
            LEFT JOIN iris.building_epc_analytics bea ON bwa.uprn = bea.uprn
            ORDER BY bwa.uprn, bea.lodgement_date DESC NULLS LAST
        )
        WITH NO DATA;
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_uprn_idx
        ON iris.building_extreme_weather_analytics (uprn);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_point_idx
        ON iris.building_extreme_weather_analytics USING GIST (point);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_region_name_idx
        ON iris.building_extreme_weather_analytics (region_name);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_county_name_idx
        ON iris.building_extreme_weather_analytics (county_name);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_district_name_idx
        ON iris.building_extreme_weather_analytics (district_name);
    """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_ward_name_idx
        ON iris.building_extreme_weather_analytics (ward_name);
    """
    )


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics_aggregates;
        """
    )

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_extreme_weather_analytics;
        """
    )

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_epc_analytics
        AS (
            WITH active_epcs AS (
                SELECT DISTINCT ON (epc_assessment.uprn) epc_assessment.id,
                    epc_assessment.uprn,
                    epc_assessment.epc_rating,
                    epc_assessment.lodgement_date,
                    epc_assessment.sap_rating,
                    epc_assessment.expiry_date
                FROM iris.epc_assessment
                WHERE epc_assessment.lodgement_date IS NOT NULL AND epc_assessment.expiry_date >= CURRENT_DATE
                ORDER BY epc_assessment.uprn, epc_assessment.lodgement_date DESC
            ), year_end_dates AS (
                SELECT generate_series(date_trunc('year'::text, (( SELECT min(epc_assessment.lodgement_date) AS min
                FROM iris.epc_assessment
                WHERE epc_assessment.lodgement_date IS NOT NULL))::timestamp with time zone)::date + '1 year'::interval - '1 day'::interval, date_trunc('year'::text, CURRENT_DATE::timestamp with time zone)::date + '1 year'::interval - '1 day'::interval, '1 year'::interval)::date AS snapshot_date
            ), snapshot_lookup AS (
                WITH epc_snapshots AS (
                    SELECT ea_1.uprn,
                        ea_1.lodgement_date,
                        yed.snapshot_date,
                        row_number() OVER (
                            PARTITION BY ea_1.uprn, yed.snapshot_date ORDER BY ea_1.lodgement_date DESC
                        ) AS rn
                    FROM iris.epc_assessment ea_1
                    CROSS JOIN year_end_dates yed
                    WHERE ea_1.lodgement_date <= yed.snapshot_date AND ea_1.expiry_date >= yed.snapshot_date AND ea_1.lodgement_date IS NOT NULL AND ea_1.expiry_date IS NOT NULL
            )
                SELECT epc_snapshots.uprn,
                    epc_snapshots.lodgement_date,
                    array_agg(epc_snapshots.snapshot_date ORDER BY epc_snapshots.snapshot_date) AS active_snapshots
                FROM epc_snapshots
                WHERE epc_snapshots.rn = 1
                GROUP BY epc_snapshots.uprn, epc_snapshots.lodgement_date
            )
            SELECT b.uprn,
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
            LEFT JOIN iris.structure_unit su_build ON su_build.uprn = b.uprn AND su_build.epc_assessment_id IS NULL AND ea.id IS NULL
            JOIN iris.boundary_line_ceremonial_counties blcc ON st_contains(blcc.geometry, b.point)
            JOIN iris.district_borough_unitary dbu ON st_contains(dbu.geometry, b.point)
            LEFT JOIN iris.district_borough_unitary_ward dbuw ON st_contains(dbuw.geometry, b.point)
            LEFT JOIN iris.unitary_electoral_division ued ON st_contains(ued.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        ) WITH NO DATA;
        """
    )

    _create_indices()

    _create_building_epc_analytics_aggregates_view()

    _create_building_extreme_weather_analytics_view()


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics_aggregates;
        """
    )

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_extreme_weather_analytics;
        """
    )

    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_epc_analytics
        AS (
            WITH active_epcs AS (
                SELECT DISTINCT ON (epc_assessment.uprn) epc_assessment.id,
                    epc_assessment.uprn,
                    epc_assessment.epc_rating,
                    epc_assessment.lodgement_date,
                    epc_assessment.sap_rating,
                    epc_assessment.expiry_date
                FROM iris.epc_assessment
                WHERE epc_assessment.lodgement_date IS NOT NULL AND epc_assessment.expiry_date >= CURRENT_DATE
                ORDER BY epc_assessment.uprn, epc_assessment.lodgement_date DESC
            ), year_end_dates AS (
                SELECT generate_series(date_trunc('year'::text, (( SELECT min(epc_assessment.lodgement_date) AS min
                FROM iris.epc_assessment
                WHERE epc_assessment.lodgement_date IS NOT NULL))::timestamp with time zone)::date + '1 year'::interval - '1 day'::interval, date_trunc('year'::text, CURRENT_DATE::timestamp with time zone)::date + '1 year'::interval - '1 day'::interval, '1 year'::interval)::date AS snapshot_date
            ), snapshot_lookup AS (
                WITH epc_snapshots AS (
                    SELECT ea_1.uprn,
                        ea_1.lodgement_date,
                        yed.snapshot_date,
                        row_number() OVER (
                            PARTITION BY ea_1.uprn, yed.snapshot_date ORDER BY ea_1.lodgement_date DESC
                        ) AS rn
                    FROM iris.epc_assessment ea_1
                    CROSS JOIN year_end_dates yed
                    WHERE ea_1.lodgement_date <= yed.snapshot_date AND ea_1.expiry_date >= yed.snapshot_date AND ea_1.lodgement_date IS NOT NULL AND ea_1.expiry_date IS NOT NULL
            )
                SELECT epc_snapshots.uprn,
                    epc_snapshots.lodgement_date,
                    array_agg(epc_snapshots.snapshot_date ORDER BY epc_snapshots.snapshot_date) AS active_snapshots
                FROM epc_snapshots
                WHERE epc_snapshots.rn = 1
                GROUP BY epc_snapshots.uprn, epc_snapshots.lodgement_date
            )
            SELECT b.uprn,
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
            LEFT JOIN iris.structure_unit su_build ON su_build.uprn = b.uprn AND su_build.epc_assessment_id IS NULL AND ea.id IS NULL
            JOIN iris.boundary_line_ceremonial_counties blcc ON st_intersects(blcc.geometry, b.point)
            JOIN iris.district_borough_unitary dbu ON st_intersects(dbu.geometry, b.point)
            LEFT JOIN iris.district_borough_unitary_ward dbuw ON st_intersects(dbuw.geometry, b.point)
            LEFT JOIN iris.unitary_electoral_division ued ON st_intersects(ued.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        ) WITH NO DATA;
        """
    )

    _create_indices()

    _create_building_epc_analytics_aggregates_view()

    _create_building_extreme_weather_analytics_view()
