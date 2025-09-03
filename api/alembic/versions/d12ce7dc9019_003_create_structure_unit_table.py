# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""003_create_structure_unit_table

Revision ID: d12ce7dc9019
Revises: e4517d52c442
Create Date: 2025-06-05 14:53:26.823304

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d12ce7dc9019"
down_revision: Union[str, None] = "e4517d52c442"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE iris.structure_unit(
            epc_assessment_id UUID,
            type VARCHAR(20),
            built_form VARCHAR(25),
            fuel_type TEXT,
            window_glazing TEXT,
            wall_construction TEXT,
            wall_insulation TEXT,
            roof_construction TEXT,
            roof_insulation TEXT,
            roof_insulation_thickness TEXT,
            floor_construction TEXT,
            floor_insulation TEXT
        );
    """
    )

    op.execute(
        """
        ALTER TABLE iris.structure_unit
        ADD CONSTRAINT fk_epc_assessment_id FOREIGN KEY (epc_assessment_id) REFERENCES iris.epc_assessment(id) ON DELETE CASCADE;
    """
    )

    op.execute(
        """
        CREATE INDEX idx_structure_unit_epc ON iris.structure_unit(epc_assessment_id);
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP INDEX IF EXISTS idx_structure_unit_epc;
    """
    )

    op.execute(
        """
        ALTER TABLE iris.structure_unit
        DROP CONSTRAINT fk_epc_assessment_id;
               """
    )

    op.execute(
        """
        DROP TABLE iris.structure_unit;
               """
    )
