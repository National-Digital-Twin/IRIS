# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""034_epc_analytics_fuel_indexes

Revision ID: 5c66700e5c72
Revises: be69024c1b9c
Create Date: 2025-11-18 12:45:58.731082

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5c66700e5c72'
down_revision: Union[str, None] = 'be69024c1b9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_fuel_types_idx
        ON iris.building_epc_analytics (region_name, type, fuel_type)
        WHERE epc_active = true AND type IS NOT NULL AND fuel_type IS NOT NULL;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_county_fuel_types_idx
        ON iris.building_epc_analytics (county_name, type, fuel_type)
        WHERE epc_active = true AND type IS NOT NULL AND fuel_type IS NOT NULL;
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_district_fuel_types_idx
        ON iris.building_epc_analytics (district_name, type, fuel_type)
        WHERE epc_active = true AND type IS NOT NULL AND fuel_type IS NOT NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_district_fuel_types_idx;")
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_county_fuel_types_idx;")
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_region_fuel_types_idx;")
