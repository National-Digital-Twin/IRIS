# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""025_create_indices_for_base_charts

Revision ID: 28c37c30e0e4
Revises: b929538f7ee1
Create Date: 2025-10-30 16:28:17.527840

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "28c37c30e0e4"
down_revision: Union[str, None] = "b929538f7ee1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
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


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP INDEX IF EXISTS building_epc_analytics_fuel_types_idx;
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS building_epc_analytics_epc_ratings_idx;
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS building_epc_analytics_region_attributes_idx;
        """
    )
