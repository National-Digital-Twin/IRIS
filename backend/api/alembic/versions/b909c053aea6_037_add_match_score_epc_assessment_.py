# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""037_add_match_score_epc_assessment_column

Revision ID: b909c053aea6
Revises: b92c77db6ba3
Create Date: 2026-01-22 15:53:51.894477

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b909c053aea6"
down_revision: Union[str, None] = "b92c77db6ba3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        ADD COLUMN match_score NUMERIC(2, 1);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        DROP COLUMN match_score;
        """
    )
