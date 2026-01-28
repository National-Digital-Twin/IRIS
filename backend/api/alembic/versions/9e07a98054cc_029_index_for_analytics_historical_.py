# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""029_index_for_analytics_historical_lookups

Revision ID: 9e07a98054cc
Revises: cf22dad02891
Create Date: 2025-11-05 13:11:48.398969

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9e07a98054cc'
down_revision: Union[str, None] = 'cf22dad02891'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_uprn_lodgement_idx;")

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_uprn_lodgement_idx
        ON iris.building_epc_analytics (uprn, lodgement_date)
        INCLUDE (sap_rating, epc_rating, type, point);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS iris.building_epc_analytics_uprn_lodgement_idx;")

    op.execute("""
        CREATE INDEX IF NOT EXISTS building_epc_analytics_uprn_lodgement_idx
        ON iris.building_epc_analytics(uprn, lodgement_date);
    """)
