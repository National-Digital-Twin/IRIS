# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""013_add_uprn_structure_unit

Revision ID: cf408e1ffd0e
Revises: 10f244f0a95e
Create Date: 2025-09-08 14:35:48.115234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf408e1ffd0e'
down_revision: Union[str, None] = '10f244f0a95e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TABLE iris.structure_unit
            ADD COLUMN uprn TEXT NULL,
            ADD COLUMN roof_shape TEXT NULL;
    """
    )

    op.execute(
        """
        ALTER TABLE iris.structure_unit
        ADD CONSTRAINT fk_building_uprn FOREIGN KEY (uprn) REFERENCES iris.building(uprn) ON DELETE CASCADE;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        ALTER TABLE iris.structure_unit
        DROP CONSTRAINT fk_building_uprn;
               """
    )

    op.execute(
        """
        ALTER TABLE iris.structure_unit
            DROP COLUMN IF EXISTS uprn,
            DROP COLUMN IF EXISTS roof_shape;
               """
    )

