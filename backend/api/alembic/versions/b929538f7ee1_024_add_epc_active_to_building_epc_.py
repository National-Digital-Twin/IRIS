# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""024_add_epc_active_to_building_epc_analytics_view

Revision ID: b929538f7ee1
Revises: 3e9303a52bf0
Create Date: 2025-10-29 11:25:08.825643

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b929538f7ee1"
down_revision: Union[str, None] = "3e9303a52bf0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_indices():
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_uprn_idx ON iris.building_epc_analytics(uprn);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_point_idx ON iris.building_epc_analytics USING GIST(point);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_region_name_idx ON iris.building_epc_analytics(region_name);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_lodgement_date_idx ON iris.building_epc_analytics(lodgement_date);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_county_name_idx ON iris.building_epc_analytics(county_name);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_district_name_idx ON iris.building_epc_analytics(district_name);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_ward_name_idx ON iris.building_epc_analytics(ward_name);
        """
    )


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_epc_analytics
        AS (
            WITH active_epcs AS (
                SELECT DISTINCT ON (uprn) *
                FROM iris.epc_assessment
                WHERE lodgement_date IS NOT NULL AND expiry_date >= CURRENT_DATE
                ORDER BY uprn, lodgement_date DESC
            )
            SELECT b.uprn,
                b.point,
                b.is_residential,
                ea.lodgement_date,
                ea.epc_rating,
                ea.sap_rating,
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
                COALESCE(er.name, sawr.name) AS region_name,
                blcc.name AS county_name,
                dbu.name AS district_name,
                COALESCE(dbuw.name, ued.name) AS ward_name,
                CASE
                    WHEN aes.id IS NOT NULL THEN true
                    ELSE false
                END AS epc_active
            FROM iris.building b
            LEFT JOIN iris.epc_assessment ea ON ea.uprn = b.uprn
            LEFT JOIN active_epcs aes ON ea.id = aes.id
            LEFT JOIN iris.structure_unit su_epc ON su_epc.epc_assessment_id = ea.id
            LEFT JOIN iris.structure_unit su_build ON su_build.uprn = b.uprn AND su_build.epc_assessment_id IS NULL AND ea.id IS NULL
            JOIN iris.boundary_line_ceremonial_counties blcc ON st_intersects(blcc.geometry, b.point)
            JOIN iris.district_borough_unitary dbu ON st_intersects(dbu.geometry, b.point)
            LEFT JOIN iris.district_borough_unitary_ward dbuw ON st_intersects(dbuw.geometry, b.point)
            LEFT JOIN iris.unitary_electoral_division ued ON st_intersects(ued.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        )
        WITH NO DATA;
        """
    )

    _create_indices()

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS building_epc_analytics_epc_active_idx ON iris.building_epc_analytics(epc_active)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.building_epc_analytics;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_epc_analytics
        AS (
            SELECT b.uprn,
                b.point,
                b.is_residential,
                ea.lodgement_date,
                ea.epc_rating,
                ea.sap_rating,
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
                COALESCE(er.name, sawr.name) AS region_name,
                blcc.name AS county_name,
                dbu.name AS district_name,
                COALESCE(dbuw.name, ued.name) AS ward_name
            FROM iris.building b
            LEFT JOIN iris.epc_assessment ea ON ea.uprn = b.uprn
            LEFT JOIN iris.structure_unit su_epc ON su_epc.epc_assessment_id = ea.id
            LEFT JOIN iris.structure_unit su_build ON su_build.uprn = b.uprn AND su_build.epc_assessment_id IS NULL AND ea.id IS NULL
            JOIN iris.boundary_line_ceremonial_counties blcc ON st_intersects(blcc.geometry, b.point)
            JOIN iris.district_borough_unitary dbu ON st_intersects(dbu.geometry, b.point)
            LEFT JOIN iris.district_borough_unitary_ward dbuw ON st_intersects(dbuw.geometry, b.point)
            LEFT JOIN iris.unitary_electoral_division ued ON st_intersects(ued.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        )
        WITH NO DATA;
        """
    )

    _create_indices()
