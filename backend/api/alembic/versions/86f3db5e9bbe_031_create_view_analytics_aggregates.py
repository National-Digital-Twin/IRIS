# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""031_create_view_analytics_aggregates

Revision ID: 86f3db5e9bbe
Revises: 5d3b574055a5
Create Date: 2025-11-07 12:11:19.381293

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '86f3db5e9bbe'
down_revision: Union[str, None] = '5d3b574055a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create building_epc_analytics_aggregates materialized view."""

    op.execute("""
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
    """)

    op.execute("""
        CREATE INDEX building_epc_analytics_aggregates_snapshot_date_idx
        ON iris.building_epc_analytics_aggregates(snapshot_date);
    """)

    op.execute("""
        CREATE INDEX building_epc_analytics_aggregates_region_snapshot_idx
        ON iris.building_epc_analytics_aggregates(region_name, snapshot_date);
    """)

    op.execute("""
        CREATE INDEX building_epc_analytics_aggregates_county_snapshot_idx
        ON iris.building_epc_analytics_aggregates(county_name, snapshot_date);
    """)

    op.execute("""
        CREATE INDEX building_epc_analytics_aggregates_district_snapshot_idx
        ON iris.building_epc_analytics_aggregates(district_name, snapshot_date);
    """)

    op.execute("""
        CREATE INDEX building_epc_analytics_aggregates_ward_snapshot_idx
        ON iris.building_epc_analytics_aggregates(ward_name, snapshot_date);
    """)

    op.execute("""
        CREATE INDEX building_epc_analytics_aggregates_snapshot_type_idx
        ON iris.building_epc_analytics_aggregates(snapshot_date, type);
    """)


def downgrade() -> None:
    """Drop the aggregates materialized view."""
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics_aggregates CASCADE;
    """)
