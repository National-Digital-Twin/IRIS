# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""033_epc_analytics_active_indexes

Revision ID: be69024c1b9c
Revises: 4137d5faffb3
Create Date: 2025-11-17 14:13:47.589788

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'be69024c1b9c'
down_revision: Union[str, None] = '4137d5faffb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_point_active_idx
        ON iris.building_epc_analytics USING GIST(point)
        WHERE epc_active = true;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_name_active_idx
        ON iris.building_epc_analytics (region_name)
        WHERE epc_active = true;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_county_name_active_idx
        ON iris.building_epc_analytics (county_name)
        WHERE epc_active = true;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_district_name_active_idx
        ON iris.building_epc_analytics (district_name)
        WHERE epc_active = true;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_ward_name_active_idx
        ON iris.building_epc_analytics (ward_name)
        WHERE epc_active = true;
    """)


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_ward_name_active_idx;")
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_district_name_active_idx;")
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_county_name_active_idx;")
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_region_name_active_idx;")
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_point_active_idx;")
