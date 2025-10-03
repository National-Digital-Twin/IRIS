# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""add region link to district_borough_unitary

Revision ID: 37989279ce33
Revises: 0e6126841f0c
Create Date: 2025-10-02 12:04:32.313209

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "37989279ce33"
down_revision: Union[str, None] = "0e6126841f0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add english_region_fid and scotland_and_wales_region_fid columns to district borough unitary table
    and assign it a value based on location
    """
    op.execute(
        """
        ALTER TABLE iris.district_borough_unitary
        ADD COLUMN english_region_fid INTEGER,
        ADD COLUMN scotland_and_wales_region_fid INTEGER,
        ADD CONSTRAINT english_region_fid_fk FOREIGN KEY(english_region_fid) REFERENCES iris.english_region(fid),
        ADD CONSTRAINT scotland_and_wales_region_fid_fk FOREIGN KEY(scotland_and_wales_region_fid) REFERENCES iris.scotland_and_wales_region(fid);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE iris.district_borough_unitary
        DROP CONSTRAINT english_region_fid_fk,
        DROP CONSTRAINT scotland_and_wales_region_fid_fk;
        """
    )

    op.execute(
        """
        ALTER TABLE iris.district_borough_unitary
        DROP COLUMN english_region_fid,
        DROP COLUMN scotland_and_wales_region_fid;
        """
    )
