# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""041_create_building_weather_analytics_aggregates_view

Revision ID: c12c1758afac
Revises: db527e1274ec
Create Date: 2026-02-24 16:40:19.387771

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c12c1758afac"
down_revision: Union[str, None] = "db527e1274ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_weather_analytics_aggregates AS (
            SELECT
                bea.region_name,
                bea.county_name,
                bea.district_name,
                bea.ward_name,
                AVG(bwa.average_daily_sunlight_hours) AS average_daily_sunlight_hours
            FROM iris.building_weather_analytics bwa
            JOIN iris.building_epc_analytics bea ON bwa.uprn = bea.uprn
            GROUP BY bea.ward_name, bea.district_name, bea.county_name, bea.region_name
        ) WITH NO DATA;
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_weather_analytics_aggregates_region_name_ix
        ON iris.building_weather_analytics_aggregates(region_name);
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_weather_analytics_aggregates_county_name_ix
        ON iris.building_weather_analytics_aggregates(county_name);
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_weather_analytics_aggregates_district_name_ix
        ON iris.building_weather_analytics_aggregates(district_name);
        """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_weather_analytics_aggregates_ward_name_ix
        ON iris.building_weather_analytics_aggregates(ward_name);
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS iris.building_weather_analytics_aggregates;
        """)
