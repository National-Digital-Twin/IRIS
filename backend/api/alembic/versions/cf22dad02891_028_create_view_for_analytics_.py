# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""028_create_view_for_analytics_historical_lookups

Revision ID: cf22dad02891
Revises: a83943138c33
Create Date: 2025-11-03 13:15:34.854944

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'cf22dad02891'
down_revision: Union[str, None] = 'a83943138c33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create normalized materialized view for historical EPC snapshots."""

    # composite index on building_epc_analytics for efficient joins
    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_uprn_lodgement_idx
        ON iris.building_epc_analytics(uprn, lodgement_date);
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW iris.building_epc_active_by_year AS
        WITH RECURSIVE date_range AS (
            -- Generate range of years from earliest EPC to current year (Dec 31st)
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
            -- For each year-end date and UPRN, find which EPC certificate was active
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


def downgrade() -> None:
    """Drop the materialized view and its indexes."""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_active_by_year CASCADE;")
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_uprn_lodgement_idx;")
