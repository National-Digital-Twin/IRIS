# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""000_create_schema_and_enable_postgis

Revision ID: 447db7945a72
Revises:
Create Date: 2025-06-02 17:28:37.347213

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "447db7945a72"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE SCHEMA IF NOT EXISTS iris;
    """
    )

    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS postgis SCHEMA iris;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP EXTENSION IF EXISTS postgis SCHEMA iris CASCADE;
               """
    )

    op.execute(
        """
        DROP SCHEMA IF EXISTS iris CASCADE;
               """
    )
