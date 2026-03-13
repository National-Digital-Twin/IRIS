# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""026_update_weather_analytics_view

Revision ID: 67aaf92accd2
Revises: 28c37c30e0e4
Create Date: 2025-10-31 23:34:09.454308

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "67aaf92accd2"
down_revision: Union[str, None] = "28c37c30e0e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_indices():
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


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_weather_analytics;
        """
    )

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

    _create_indices()


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_weather_analytics;
        """
    )

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
        )
        WITH NO DATA;
        """
    )

    _create_indices()
