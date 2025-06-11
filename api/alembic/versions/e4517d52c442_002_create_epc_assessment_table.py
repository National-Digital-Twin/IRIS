# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""002_create_epc_assessment_table

Revision ID: e4517d52c442
Revises: 0cba3d41c22e
Create Date: 2025-06-05 14:44:50.804348

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e4517d52c442"
down_revision: Union[str, None] = "0cba3d41c22e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE iris.epc_assessment(
            id UUID PRIMARY KEY,
            uprn TEXT,
            epc_rating CHAR(1),
            lodgement_date DATE
        );
    """
    )

    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        ADD CONSTRAINT fk_uprn_building FOREIGN KEY (uprn) REFERENCES iris.building (uprn) ON DELETE NO ACTION;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE iris.epc_assessment
        DROP CONSTRAINT fk_uprn_building;
               """
    )

    op.execute(
        """
        DROP TABLE iris.epc_assessment;
               """
    )
