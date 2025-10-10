# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""018_create_view_for_analytics_dashboard

Revision ID: b55e05000f66
Revises: b0c5faee6d07
Create Date: 2025-10-10 10:45:39.530115

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b55e05000f66"
down_revision: Union[str, None] = "b0c5faee6d07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # COALESCE picks structure_unit data from EPC path if available, otherwise from building path
    # This handles both buildings with EPC assessments (via su_epc) and without (via su_build)
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.analytics
        AS (
            SELECT
                b.uprn,
                b.point,
                b.is_residential,
                ea.lodgement_date,
                ea.epc_rating,
                ea.sap_score,
                ea.expiry_date,
                COALESCE(su_epc.type, su_build.type) AS type,
                COALESCE(su_epc.built_form, su_build.built_form) AS built_form,
                COALESCE(su_epc.fuel_type, su_build.fuel_type) AS fuel_type,
                COALESCE(su_epc.window_glazing, su_build.window_glazing) AS window_glazing,
                COALESCE(su_epc.wall_construction, su_build.wall_construction) AS wall_construction,
                COALESCE(su_epc.wall_insulation, su_build.wall_insulation) AS wall_insulation,
                COALESCE(su_epc.roof_construction, su_build.roof_construction) AS roof_construction,
                COALESCE(su_epc.roof_insulation, su_build.roof_insulation) AS roof_insulation,
                COALESCE(su_epc.roof_insulation_thickness, su_build.roof_insulation_thickness) AS roof_insulation_thickness,
                COALESCE(su_epc.floor_construction, su_build.floor_construction) AS floor_construction,
                COALESCE(su_epc.floor_insulation, su_build.floor_insulation) AS floor_insulation,
                COALESCE(su_epc.has_roof_solar_panels, su_build.has_roof_solar_panels) AS has_roof_solar_panels,
                COALESCE(su_epc.roof_material, su_build.roof_material) AS roof_material,
                COALESCE(su_epc.roof_aspect_area_facing_north_m2, su_build.roof_aspect_area_facing_north_m2) AS roof_aspect_area_facing_north_m2,
                COALESCE(su_epc.roof_aspect_area_facing_east_m2, su_build.roof_aspect_area_facing_east_m2) AS roof_aspect_area_facing_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_m2, su_build.roof_aspect_area_facing_south_m2) AS roof_aspect_area_facing_south_m2,
                COALESCE(su_epc.roof_aspect_area_facing_west_m2, su_build.roof_aspect_area_facing_west_m2) AS roof_aspect_area_facing_west_m2,
                COALESCE(su_epc.roof_aspect_area_facing_north_east_m2, su_build.roof_aspect_area_facing_north_east_m2) AS roof_aspect_area_facing_north_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_east_m2, su_build.roof_aspect_area_facing_south_east_m2) AS roof_aspect_area_facing_south_east_m2,
                COALESCE(su_epc.roof_aspect_area_facing_south_west_m2, su_build.roof_aspect_area_facing_south_west_m2) AS roof_aspect_area_facing_south_west_m2,
                COALESCE(su_epc.roof_aspect_area_facing_north_west_m2, su_build.roof_aspect_area_facing_north_west_m2) AS roof_aspect_area_facing_north_west_m2,
                COALESCE(su_epc.roof_aspect_area_indeterminable_m2, su_build.roof_aspect_area_indeterminable_m2) AS roof_aspect_area_indeterminable_m2,
                COALESCE(su_epc.roof_shape, su_build.roof_shape) AS roof_shape,
                COALESCE(er.name, sawr.name) AS region_name
            FROM iris.building b
            LEFT JOIN iris.epc_assessment ea ON ea.uprn = b.uprn
            LEFT JOIN iris.structure_unit su_epc ON su_epc.epc_assessment_id = ea.id
            LEFT JOIN iris.structure_unit su_build
                ON su_build.uprn = b.uprn
                AND su_build.epc_assessment_id IS NULL
                AND ea.id IS NULL
            JOIN iris.district_borough_unitary dbu ON ST_INTERSECTS(dbu.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        )
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS uprn_ix ON iris.analytics(uprn);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS point_ix ON iris.analytics USING GIST(point);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS region_name_ix ON iris.analytics(region_name);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS lodgement_date_ix ON iris.analytics(lodgement_date);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop materialized view (automatically drops all its indexes)
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.analytics;
        """
    )
