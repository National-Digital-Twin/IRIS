# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""023_update_and_split_analytics_view

Revision ID: 3e9303a52bf0
Revises: 47ed09fc85cc
Create Date: 2025-10-24 13:57:09.344870

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3e9303a52bf0"
down_revision: Union[str, None] = "47ed09fc85cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_indices(view: str) -> None:
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS uprn_ix ON iris.{view}(uprn);
        """
    )

    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS point_ix ON iris.{view} USING GIST(point);
        """
    )

    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS region_name_ix ON iris.{view}(region_name);
        """
    )

    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS lodgement_date_ix ON iris.{view}(lodgement_date);
        """
    )


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DROP MATERIALIZED VIEW IF EXISTS iris.analytics;
    """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_epc_analytics
        AS (
            SELECT
                b.uprn,
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
            LEFT JOIN iris.structure_unit su_build
                ON su_build.uprn = b.uprn
                AND su_build.epc_assessment_id IS NULL
                AND ea.id IS NULL
            JOIN iris.boundary_line_ceremonial_counties blcc ON ST_INTERSECTS(blcc.geometry, b.point)
            JOIN iris.district_borough_unitary dbu ON ST_INTERSECTS(dbu.geometry, b.point)
            LEFT JOIN iris.district_borough_unitary_ward dbuw ON ST_INTERSECTS(dbuw.geometry, b.point)
            LEFT JOIN iris.unitary_electoral_division ued ON ST_INTERSECTS(ued.geometry, b.point)
            LEFT JOIN iris.english_region er ON er.fid = dbu.english_region_fid
            LEFT JOIN iris.scotland_and_wales_region sawr ON sawr.fid = dbu.scotland_and_wales_region_fid
            WHERE su_epc.epc_assessment_id IS NOT NULL OR su_build.uprn IS NOT NULL
        )
        WITH NO DATA;
    """
    )

    _create_indices("building_epc_analytics")

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS county_name_ix ON iris.building_epc_analytics(county_name);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS district_name_ix ON iris.building_epc_analytics(district_name);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ward_name_ix ON iris.building_epc_analytics(ward_name);
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS iris.building_weather_analytics
        AS (
            WITH wdrp_0 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 0
            ),
            wdrp_45 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 45
            ),
            wdrp_90 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 90
            ),
            wdrp_135 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 135
            ),
            wdrp_180 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 180
            ),
            wdrp_225 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 225
            ),
            wdrp_270 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 270
            ),
            wdrp_315 AS (
                SELECT wdr_40_median, shape
                FROM iris.wind_driven_rain_projections
                WHERE wall_orientation = 315
            )
            SELECT
                b.uprn,
                b.point,
                acoid.icingdays as icing_days,
                wdrp_0.wdr_40_median as wdr_40_median_0,
                wdrp_45.wdr_40_median as wdr_40_median_45,
                wdrp_90.wdr_40_median as wdr_40_median_90,
                wdrp_135.wdr_40_median as wdr_40_median_135,
                wdrp_180.wdr_40_median as wdr_40_median_180,
                wdrp_225.wdr_40_median as wdr_40_median_225,
                wdrp_270.wdr_40_median as wdr_40_median_270,
                wdrp_315.wdr_40_median as wdr_40_median_315,
                acohdp.hsd_40_median
            FROM iris.building b
            JOIN iris.annual_count_of_icing_days_1991_2020 acoid ON ST_CONTAINS(acoid.shape, b.point)
            JOIN wdrp_0 ON ST_CONTAINS(wdrp_0.shape, b.point)
            JOIN wdrp_45 ON ST_CONTAINS(wdrp_45.shape, b.point)
            JOIN wdrp_90 ON ST_CONTAINS(wdrp_90.shape, b.point)
            JOIN wdrp_135 ON ST_CONTAINS(wdrp_135.shape, b.point)
            JOIN wdrp_180 ON ST_CONTAINS(wdrp_180.shape, b.point)
            JOIN wdrp_225 ON ST_CONTAINS(wdrp_225.shape, b.point)
            JOIN wdrp_270 ON ST_CONTAINS(wdrp_270.shape, b.point)
            JOIN wdrp_315 ON ST_CONTAINS(wdrp_315.shape, b.point)
            JOIN iris.annual_count_of_hot_summer_days_projections_12km acohdp ON ST_CONTAINS(acohdp.shape, b.point)
        )
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS uprn_ix ON iris.building_weather_analytics(uprn);
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS point_ix ON iris.building_weather_analytics USING GIST(point);
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
        DROP MATERIALIZED VIEW IF EXISTS iris.building_weather_analytics;
    """
    )

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

    _create_indices("analytics")
