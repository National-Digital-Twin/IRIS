# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""017_alter_epc_assessment_add_indexes

Revision ID: b0c5faee6d07
Revises: 37989279ce33
Create Date: 2025-10-10 10:44:31.110775

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b0c5faee6d07"
down_revision: Union[str, None] = "37989279ce33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add sap_score and expiry_date columns to epc_assessment table
    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        ADD COLUMN IF NOT EXISTS sap_score INTEGER;
        """
    )
    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        ADD COLUMN IF NOT EXISTS expiry_date DATE;
        """
    )

    # Add composite unique index for upserts on (uprn, lodgement_date)
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_epc_uprn_lodgement
        ON iris.epc_assessment(uprn, lodgement_date);
        """
    )

    # Add index on expiry_date for filtering active/expired certificates
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_epc_expiry_date
        ON iris.epc_assessment(expiry_date);
        """
    )

    # Add missing index on structure_unit.uprn for join performance
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_structure_unit_uprn ON iris.structure_unit(uprn);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DROP INDEX IF EXISTS iris.idx_epc_uprn_lodgement;
        """
    )

    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        DROP COLUMN IF EXISTS sap_score;
        """
    )

    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        DROP COLUMN IF EXISTS expiry_date;
        """
    )
