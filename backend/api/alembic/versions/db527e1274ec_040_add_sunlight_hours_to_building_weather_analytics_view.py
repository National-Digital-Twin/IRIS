# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""040_add_sunlight_hours_to_building_weather_analytics_view

Revision ID: db527e1274ec
Revises: f4b7c2d9a1e3
Create Date: 2026-02-23 15:41:38.767227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db527e1274ec'
down_revision: Union[str, None] = 'f4b7c2d9a1e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_building_weather_analytics_view_indices():
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_weather_analytics_uprn_idx ON iris.building_weather_analytics(uprn);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_weather_analytics_point_idx ON iris.building_weather_analytics USING GIST(point);
        """
    )

def _drop_building_weather_analytics_view_indices():
    op.execute(
        """
        DROP INDEX IF EXISTS iris.building_weather_analytics_uprn_idx;
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.building_weather_analytics_point_idx;
        """
    )

def _create_building_weather_analytics_view() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_weather_analytics
        AS (
            WITH wdrp_0 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 0
            ),
            wdrp_45 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 45
            ),
            wdrp_90 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 90
            ),
            wdrp_135 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 135
            ),
            wdrp_180 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 180
            ),
            wdrp_225 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 225
            ),
            wdrp_270 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 270
            ),
            wdrp_315 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 315
            )
            SELECT
                b.uprn,
                b.point,
                acoid.icingdays as icing_days,
                wdrp_0.wdr_40_median as wdr_40_median_0,
                wdrp_45.wdr_40_median as wdr_40_median_45,
                wdrp_90.wdr_40_median as wdr_40_median_90,
                wdrp_135.wdr_40_median as wdr_40_median_135,
                wdrp_180.wdr_40_median as wdr_40_median_180,
                wdrp_225.wdr_40_median as wdr_40_median_225,
                wdrp_270.wdr_40_median as wdr_40_median_270,
                wdrp_315.wdr_40_median as wdr_40_median_315,
                acohdp.hsd_40_median,
                aacosh.sunlight_hours as average_annual_sunlight_hours,
                aacosh.sunlight_hours / 365.0 as average_daily_sunlight_hours
            FROM iris.building b
            JOIN iris.annual_count_of_icing_days_1991_2020 acoid ON ST_CONTAINS(acoid.shape, b.point)
            JOIN wdrp_0 ON ST_CONTAINS(wdrp_0.shape, b.point)
            JOIN wdrp_45 ON ST_CONTAINS(wdrp_45.shape, b.point)
            JOIN wdrp_90 ON ST_CONTAINS(wdrp_90.shape, b.point)
            JOIN wdrp_135 ON ST_CONTAINS(wdrp_135.shape, b.point)
            JOIN wdrp_180 ON ST_CONTAINS(wdrp_180.shape, b.point)
            JOIN wdrp_225 ON ST_CONTAINS(wdrp_225.shape, b.point)
            JOIN wdrp_270 ON ST_CONTAINS(wdrp_270.shape, b.point)
            JOIN wdrp_315 ON ST_CONTAINS(wdrp_315.shape, b.point)
            JOIN iris.annual_count_of_hot_summer_days_projections_12km acohdp ON ST_CONTAINS(acohdp.shape, b.point)
            JOIN iris.average_annual_count_of_sunlight_hours_5km aacosh ON ST_CONTAINS(aacosh.shape, b.point)
            WHERE b.is_residential = true
        )
        WITH NO DATA;
        """
    )

def _drop_building_weather_analytics_view() -> None:
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_weather_analytics;
        """
    )

def _create_building_extreme_weather_analytics_view() -> None:
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

def _drop_building_extreme_weather_analytics_view() -> None:
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_extreme_weather_analytics;
        """
    )


def upgrade() -> None:
    """Upgrade schema."""
    _drop_building_extreme_weather_analytics_view()
    _drop_building_weather_analytics_view_indices()
    _drop_building_weather_analytics_view()
    _create_building_weather_analytics_view()
    _create_building_weather_analytics_view_indices()
    _create_building_extreme_weather_analytics_view()
    # ### end Alembic commands ###

def _create_downgrade_building_weather_analytics_view() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_weather_analytics
        AS (
            WITH wdrp_0 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 0
            ),
            wdrp_45 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 45
            ),
            wdrp_90 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 90
            ),
            wdrp_135 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 135
            ),
            wdrp_180 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 180
            ),
            wdrp_225 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 225
            ),
            wdrp_270 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 270
            ),
            wdrp_315 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 315
            )
            SELECT
                b.uprn,
                b.point,
                acoid.icingdays as icing_days,
                wdrp_0.wdr_40_median as wdr_40_median_0,
                wdrp_45.wdr_40_median as wdr_40_median_45,
                wdrp_90.wdr_40_median as wdr_40_median_90,
                wdrp_135.wdr_40_median as wdr_40_median_135,
                wdrp_180.wdr_40_median as wdr_40_median_180,
                wdrp_225.wdr_40_median as wdr_40_median_225,
                wdrp_270.wdr_40_median as wdr_40_median_270,
                wdrp_315.wdr_40_median as wdr_40_median_315,
                acohdp.hsd_40_median
            FROM iris.building b
            JOIN iris.annual_count_of_icing_days_1991_2020 acoid ON ST_CONTAINS(acoid.shape, b.point)
            JOIN wdrp_0 ON ST_CONTAINS(wdrp_0.shape, b.point)
            JOIN wdrp_45 ON ST_CONTAINS(wdrp_45.shape, b.point)
            JOIN wdrp_90 ON ST_CONTAINS(wdrp_90.shape, b.point)
            JOIN wdrp_135 ON ST_CONTAINS(wdrp_135.shape, b.point)
            JOIN wdrp_180 ON ST_CONTAINS(wdrp_180.shape, b.point)
            JOIN wdrp_225 ON ST_CONTAINS(wdrp_225.shape, b.point)
            JOIN wdrp_270 ON ST_CONTAINS(wdrp_270.shape, b.point)
            JOIN wdrp_315 ON ST_CONTAINS(wdrp_315.shape, b.point)
            JOIN iris.annual_count_of_hot_summer_days_projections_12km acohdp ON ST_CONTAINS(acohdp.shape, b.point)
            WHERE b.is_residential = true
        )
        WITH NO DATA;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    _drop_building_extreme_weather_analytics_view()
    _drop_building_weather_analytics_view_indices()
    _drop_building_weather_analytics_view()
    _create_downgrade_building_weather_analytics_view()
    _create_building_weather_analytics_view_indices()
    _create_building_extreme_weather_analytics_view()
