# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""032_recreate_extreme_weather_view

Revision ID: 4137d5faffb3
Revises: 86f3db5e9bbe
Create Date: 2025-11-12 14:57:16.032597

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4137d5faffb3'
down_revision: Union[str, None] = '86f3db5e9bbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Recreate building_extreme_weather_analytics with geographic area columns."""

    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.building_extreme_weather_analytics CASCADE;
    """)

    op.execute("""
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
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_uprn_idx
        ON iris.building_extreme_weather_analytics (uprn);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_point_idx
        ON iris.building_extreme_weather_analytics USING GIST (point);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_region_name_idx
        ON iris.building_extreme_weather_analytics (region_name);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_county_name_idx
        ON iris.building_extreme_weather_analytics (county_name);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_district_name_idx
        ON iris.building_extreme_weather_analytics (district_name);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_ward_name_idx
        ON iris.building_extreme_weather_analytics (ward_name);
    """)


def downgrade() -> None:
    """Revert to original building_extreme_weather_analytics view."""

    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.building_extreme_weather_analytics CASCADE;
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_extreme_weather_analytics AS (
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
            SELECT bwa.uprn, bwa.point, babi.affected as affected_by_icing_days,
                babh.affected as affected_by_hsds, babw.affected as affected_by_wdr
            FROM iris.building_weather_analytics bwa
            LEFT JOIN buildings_affected_by_icing_days babi ON bwa.uprn = babi.uprn
            LEFT JOIN buildings_affected_by_hsds babh ON bwa.uprn = babh.uprn
            LEFT JOIN buildings_affected_by_wdrp babw ON bwa.uprn = babw.uprn
        )
        WITH NO DATA;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_uprn_idx
        ON iris.building_extreme_weather_analytics (uprn);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_extreme_weather_analytics_point_idx
        ON iris.building_extreme_weather_analytics USING GIST (point);
    """)

