# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""036_updating_building_epc_analytics_indices

Revision ID: b92c77db6ba3
Revises: 44de9a59d873
Create Date: 2026-01-14 13:28:51.347954

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b92c77db6ba3"
down_revision: Union[str, None] = "44de9a59d873"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DROP INDEX IF EXISTS iris.building_epc_analytics_region_attributes_idx;
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.building_epc_analytics_region_fuel_types_idx;
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
            wall_construction,
            epc_rating
        )
        WHERE epc_active = true;
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_fuel_types_idx
        ON iris.building_epc_analytics (region_name, type, fuel_type, epc_rating)
        WHERE epc_active = true AND type IS NOT NULL AND fuel_type IS NOT NULL;
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP INDEX IF EXISTS iris.building_epc_analytics_region_attributes_idx;
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS iris.building_epc_analytics_region_fuel_types_idx;
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
            wall_construction,
        )
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
    # ### end Alembic commands ###
