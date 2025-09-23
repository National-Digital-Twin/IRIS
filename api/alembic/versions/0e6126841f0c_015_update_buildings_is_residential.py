# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""update_buildings_is_residential

Revision ID: 0e6126841f0c
Revises: cc816c325e2a
Create Date: 2025-09-17 13:39:21.303885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e6126841f0c'
down_revision: Union[str, None] = 'cc816c325e2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.execute(sa.text("SET LOCAL application_name = 'alembic_015_is_residential';"))
    op.execute(sa.text("SET LOCAL lock_timeout = '5s';"))
    op.execute(sa.text("SET LOCAL statement_timeout = '1h';"))

    
    op.execute(
        """
        ALTER TABLE iris.building ADD COLUMN "is_residential" BOOLEAN not null DEFAULT false;
        """
    )

    op.execute(
        """
        UPDATE iris.building AS b
        SET is_residential = TRUE
              WHERE EXISTS (
                  SELECT 1 FROM iris.epc_assessment AS ea
                  WHERE ea.uprn = b.uprn);
    """
    )
    
    op.execute(
        """
           UPDATE iris.building AS b
           SET is_residential = TRUE
           WHERE is_residential = FALSE AND EXISTS (
                  SELECT 1
                  FROM iris.structure_unit AS su
                  WHERE su.uprn = b.uprn
              );
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    
    op.execute(sa.text("SET LOCAL application_name = 'alembic_015_is_residential';"))
    op.execute(sa.text("SET LOCAL lock_timeout = '5s';"))
    op.execute(sa.text("SET LOCAL statement_timeout = '1h';"))

    
    op.execute(
        """
        ALTER TABLE iris.building DROP COLUMN "is_residential";
        """
    )
    