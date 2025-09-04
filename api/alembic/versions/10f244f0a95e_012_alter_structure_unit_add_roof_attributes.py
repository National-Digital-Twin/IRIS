# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""012_alter_structure_unit_add_roof_attributes

Revision ID: 10f244f0a95e
Revises: d99eb3e1e4ab
Create Date: 2025-08-21 10:31:46.144023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10f244f0a95e'
down_revision: Union[str, None] = 'd99eb3e1e4ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    """ Alter table DROP COLUMN IF EXISTS."""
    op.execute(
        """
        ALTER TABLE iris.structure_unit
            ADD COLUMN has_roof_solar_panels BOOLEAN NULL,
            ADD COLUMN roof_material TEXT NULL,
            ADD COLUMN roof_aspect_area_facing_north_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_facing_east_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_facing_south_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_facing_west_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_facing_north_east_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_facing_south_east_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_facing_south_west_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_facing_north_west_m2 DOUBLE PRECISION NULL,
            ADD COLUMN roof_aspect_area_indeterminable_m2 DOUBLE PRECISION NULL;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    """ Alter table DROP COLUMN IF EXISTSs."""
    op.execute(
        """
        ALTER TABLE iris.structure_unit
            DROP COLUMN IF EXISTS has_roof_solar_panels,
            DROP COLUMN IF EXISTS roof_material,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_north_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_east_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_south_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_west_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_north_east_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_south_east_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_south_west_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_facing_north_west_m2,
            DROP COLUMN IF EXISTS roof_aspect_area_indeterminable_m2;
    """
    )

