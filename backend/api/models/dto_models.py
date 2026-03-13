# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
import datetime
from typing import List, Optional

import pydantic
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel

from .ies_models import IesThing
from .utils import get_nullable_float

print(pydantic.VERSION)


def to_camel(field: str) -> str:
    if field.lower() == "uprn" or field.lower() == "toid":
        return field.upper()
    parts = field.split("_")
    return "".join(word.capitalize() for word in parts[0:])


class AccessUser(BaseModel):
    username: str
    user_id: str
    active: Optional[bool] = None
    email: Optional[str] = None
    attributes: dict[str, str]
    groups: List[str]


class Building(IesThing):
    uprn: Optional[str] = None
    structure_unit_type: Optional[str] = None


class DetailedBuilding(Building):
    post_code: Optional[str] = None
    lodgement_date: Optional[str] = None
    sap_rating: Optional[float] = None
    built_form: Optional[str] = None
    floor_construction: Optional[str] = None
    floor_insulation: Optional[str] = None
    roof_construction: Optional[str] = None
    roof_insulation_location: Optional[str] = None
    roof_insulation_thickness: Optional[str] = None
    wall_construction: Optional[str] = None
    wall_insulation: Optional[str] = None
    window_glazing: Optional[str] = None
    fueltype: Optional[str] = None
    # OS NGD Buildings attributes
    roof_material: Optional[str] = None
    solar_panel_presence: Optional[str] = None
    roof_shape: Optional[str] = None
    # Roof aspect areas (square meters) by direction
    roof_aspect_area_facing_north_m2: Optional[float] = None
    roof_aspect_area_facing_north_east_m2: Optional[float] = None
    roof_aspect_area_facing_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_m2: Optional[float] = None
    roof_aspect_area_facing_south_west_m2: Optional[float] = None
    roof_aspect_area_facing_west_m2: Optional[float] = None
    roof_aspect_area_facing_north_west_m2: Optional[float] = None
    roof_aspect_area_indeterminable_m2: Optional[float] = None


class DetailedBuildingSchema(DetailedBuilding):
    @classmethod
    def from_orm(cls, obj):
        return cls(
            solar_panel_presence=str(obj.has_roof_solar_panels),
            roof_material=obj.roof_material,
            roof_shape=obj.roof_shape,
            roof_aspect_area_facing_north_m2=get_nullable_float(
                obj.roof_aspect_area_facing_north_m2
            ),
            roof_aspect_area_facing_north_east_m2=get_nullable_float(
                obj.roof_aspect_area_facing_north_east_m2
            ),
            roof_aspect_area_facing_east_m2=get_nullable_float(
                obj.roof_aspect_area_facing_east_m2
            ),
            roof_aspect_area_facing_south_east_m2=get_nullable_float(
                obj.roof_aspect_area_facing_south_east_m2
            ),
            roof_aspect_area_facing_south_m2=get_nullable_float(
                obj.roof_aspect_area_facing_south_m2
            ),
            roof_aspect_area_facing_south_west_m2=get_nullable_float(
                obj.roof_aspect_area_facing_south_west_m2
            ),
            roof_aspect_area_facing_west_m2=get_nullable_float(
                obj.roof_aspect_area_facing_west_m2
            ),
            roof_aspect_area_facing_north_west_m2=get_nullable_float(
                obj.roof_aspect_area_facing_north_west_m2
            ),
            roof_aspect_area_indeterminable_m2=get_nullable_float(
                obj.roof_aspect_area_indeterminable_m2
            ),
        )


class FilterableBuilding(BaseModel):
    uprn: Optional[str] = None
    postcode: Optional[str] = None
    lodgement_date: Optional[str] = None
    built_form: Optional[str] = None
    fuel_type: Optional[str] = None
    floor_construction: Optional[str] = None
    floor_insulation: Optional[str] = None
    roof_construction: Optional[str] = None
    roof_insulation_location: Optional[str] = None
    roof_insulation_thickness: Optional[str] = None
    wall_construction: Optional[str] = None
    wall_insulation: Optional[str] = None
    window_glazing: Optional[str] = None
    has_roof_solar_panels: Optional[bool] = None
    roof_material: Optional[str] = None
    roof_aspect_area_facing_north: Optional[float] = None
    roof_aspect_area_facing_north_east: Optional[float] = None
    roof_aspect_area_facing_east: Optional[float] = None
    roof_aspect_area_facing_south_east: Optional[float] = None
    roof_aspect_area_facing_south: Optional[float] = None
    roof_aspect_area_facing_south_west: Optional[float] = None
    roof_aspect_area_facing_west: Optional[float] = None
    roof_aspect_area_facing_north_west: Optional[float] = None


class EpcStatistics(IesThing):
    name: Optional[str] = None
    a_rating: Optional[int] = 0
    b_rating: Optional[int] = 0
    c_rating: Optional[int] = 0
    d_rating: Optional[int] = 0
    e_rating: Optional[int] = 0
    f_rating: Optional[int] = 0
    g_rating: Optional[int] = 0
    no_rating: Optional[int] = 0


class FlaggedBuilding(BaseModel):
    toid: Optional[str] = None
    uprn: Optional[str] = None
    flagged: Optional[str] = None

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


class FlagHistory(BaseModel):
    uprn: Optional[str] = None
    flagged: Optional[str] = None
    flag_type: Optional[str] = None
    flagged_by_name: Optional[str] = None
    flag_date: Optional[str] = None
    assessment_date: Optional[str] = None
    assessor_name: Optional[str] = None
    assessment_reason: Optional[str] = None

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


class SimpleBuilding(Building):
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    first_line_of_address: Optional[str] = None
    energy_rating: Optional[str] = None
    toid: Optional[str] = None


class EpcAndOsBuildingSchema(BaseModel):
    uprn: str
    first_line_of_address: str
    toid: str
    lattitude: float
    longitude: float
    epc_rating: Optional[str] = None
    structure_unit_type: Optional[str] = None

    @classmethod
    def from_orm(cls, obj):
        wkb_point = WKBElement(obj.point)
        # convert geometry to WKT format
        shape_obj = to_shape(wkb_point)
        return cls(
            uprn=obj.uprn,
            first_line_of_address=obj.first_line_of_address,
            toid=obj.toid,
            longitude=shape_obj.x,
            lattitude=shape_obj.y,
            epc_rating=obj.epc_rating,
            structure_unit_type=obj.structure_unit_type,
        )


class FilterableBuildingSchema(BaseModel):
    uprn: str
    post_code: str
    built_form: Optional[str] = None
    lodgement_date: Optional[datetime.date] = None
    fuel_type: Optional[str] = None
    window_glazing: Optional[str] = None
    wall_construction: Optional[str] = None
    wall_insulation: Optional[str] = None
    floor_construction: Optional[str] = None
    floor_insulation: Optional[str] = None
    has_roof_solar_panels: Optional[bool] = None
    roof_material: Optional[str] = None
    roof_aspect_area_facing_north_m2: Optional[float] = None
    roof_aspect_area_facing_north_east_m2: Optional[float] = None
    roof_aspect_area_facing_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_m2: Optional[float] = None
    roof_aspect_area_facing_south_west_m2: Optional[float] = None
    roof_aspect_area_facing_west_m2: Optional[float] = None
    roof_aspect_area_facing_north_west_m2: Optional[float] = None
    roof_construction: Optional[str] = None
    roof_insulation: Optional[str] = None
    roof_insulation_thickness: Optional[str] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            uprn=obj.uprn,
            post_code=obj.post_code,
            built_form=obj.built_form,
            lodgement_date=obj.lodgement_date,
            fuel_type=obj.fuel_type,
            window_glazing=obj.window_glazing,
            wall_construction=obj.wall_construction,
            wall_insulation=obj.wall_insulation,
            floor_construction=obj.floor_construction,
            floor_insulation=obj.floor_insulation,
            roof_construction=obj.roof_construction,
            roof_insulation=obj.roof_insulation,
            roof_insulation_thickness=obj.roof_insulation_thickness,
            has_roof_solar_panels=obj.has_roof_solar_panels,
            roof_material=obj.roof_material,
            roof_aspect_area_facing_north_m2=obj.roof_aspect_area_facing_north_m2,
            roof_aspect_area_facing_north_east_m2=obj.roof_aspect_area_facing_north_east_m2,
            roof_aspect_area_facing_east_m2=obj.roof_aspect_area_facing_east_m2,
            roof_aspect_area_facing_south_east_m2=obj.roof_aspect_area_facing_south_east_m2,
            roof_aspect_area_facing_south_m2=obj.roof_aspect_area_facing_south_m2,
            roof_aspect_area_facing_south_west_m2=obj.roof_aspect_area_facing_south_west_m2,
            roof_aspect_area_facing_west_m2=obj.roof_aspect_area_facing_west_m2,
            roof_aspect_area_facing_north_west_m2=obj.roof_aspect_area_facing_north_west_m2,
        )

    class Config:
        from_orm = True


class FilterSummary(BaseModel):
    postcode: set[str] = set()
    built_form: set[str] = set()
    inspection_year: set[str] = set()
    energy_rating: set[str] = {"EPC In Date", "EPC Expired"}
    fuel_type: set[str] = set()
    window_glazing: set[str] = set()
    wall_construction: set[str] = set()
    wall_insulation: set[str] = set()
    floor_construction: set[str] = set()
    floor_insulation: set[str] = set()
    has_roof_solar_panels: set[bool] = set()
    roof_material: set[str] = set()
    roof_aspect_area_direction: set[str] = set()
    roof_construction: set[str] = set()
    roof_insulation_location: set[str] = set()
    roof_insulation_thickness: set[str] = set()


class CountOfEpcRatings(BaseModel):
    epc_a: int
    epc_b: int
    epc_c: int
    epc_d: int
    epc_e: int
    epc_f: int
    epc_g: int

    @classmethod
    def from_orm(cls, obj):
        return cls(
            epc_a=obj.epc_a,
            epc_b=obj.epc_b,
            epc_c=obj.epc_c,
            epc_d=obj.epc_d,
            epc_e=obj.epc_e,
            epc_f=obj.epc_f,
            epc_g=obj.epc_g,
        )


class CountOfEpcRatingsPerRegion(CountOfEpcRatings):
    region_name: str

    @classmethod
    def from_orm(cls, obj):
        return cls(
            region_name=obj.region_name,
            epc_a=obj.epc_a,
            epc_b=obj.epc_b,
            epc_c=obj.epc_c,
            epc_d=obj.epc_d,
            epc_e=obj.epc_e,
            epc_f=obj.epc_f,
            epc_g=obj.epc_g,
        )


class EPCRatingsByCategory(BaseModel):
    name: str
    epc_a: int
    epc_b: int
    epc_c: int
    epc_d: int
    epc_e: int
    epc_f: int
    epc_g: int
    total: int

    @classmethod
    def from_orm(cls, obj):
        name = getattr(obj, "name", None) or getattr(obj, "area_name", None)
        return cls(
            name=name,
            epc_a=obj.epc_a,
            epc_b=obj.epc_b,
            epc_c=obj.epc_c,
            epc_d=obj.epc_d,
            epc_e=obj.epc_e,
            epc_f=obj.epc_f,
            epc_g=obj.epc_g,
            total=sum(
                [
                    obj.epc_a,
                    obj.epc_b,
                    obj.epc_c,
                    obj.epc_d,
                    obj.epc_e,
                    obj.epc_f,
                    obj.epc_g,
                ]
            ),
        )


class FuelTypesByBuildingType(BaseModel):
    building_type: str
    fuel_type: str
    count: int

    @classmethod
    def from_orm(cls, obj):
        return cls(
            building_type=obj.building_type,
            fuel_type=obj.fuel_type,
            count=obj.count,
        )


class AverageSapRatingPerLodgementDate(BaseModel):
    date: datetime.date
    national_avg_sap_rating: float
    filtered_avg_sap_rating: Optional[float] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            date=obj.date,
            national_avg_sap_rating=obj.national_avg_sap_rating,
            filtered_avg_sap_rating=obj.filtered_avg_sap_rating,
        )


class SapRatingTimelineDataPoint(BaseModel):
    date: datetime.date
    name: str
    avg_sap_rating: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            date=obj.date,
            name=obj.name,
            avg_sap_rating=obj.avg_sap_rating,
        )


class EpcRatingCountsOvertime(BaseModel):
    date: datetime.date
    epc_a: int
    epc_b: int
    epc_c: int
    epc_d: int
    epc_e: int
    epc_f: int
    epc_g: int

    @classmethod
    def from_orm(cls, obj):
        return cls(
            date=obj.date,
            epc_a=obj.epc_a,
            epc_b=obj.epc_b,
            epc_c=obj.epc_c,
            epc_d=obj.epc_d,
            epc_e=obj.epc_e,
            epc_f=obj.epc_f,
            epc_g=obj.epc_g,
        )


class BuildingsAffectedByExtremeWeather(BaseModel):
    number_of_buildings: int
    filtered_number_of_buildings: Optional[int] = None
    affected_by_icing_days: Optional[bool] = None
    affected_by_hsds: Optional[bool] = None
    affected_by_wdr: Optional[bool] = None

    @classmethod
    def from_orm(cls, obj, has_filter: bool = True):
        return cls(
            number_of_buildings=obj.number_of_buildings,
            filtered_number_of_buildings=(
                obj.filtered_number_of_buildings if has_filter else None
            ),
            affected_by_icing_days=obj.affected_by_icing_days,
            affected_by_hsds=obj.affected_by_hsds,
            affected_by_wdr=obj.affected_by_wdr,
        )


class NumberOfInDateAndExpiredEpcs(BaseModel):
    year: datetime.date
    expired: int
    active: int

    @classmethod
    def from_orm(cls, obj):
        return cls(year=obj.year, expired=obj.expired, active=obj.active)


class BuildingsByDeprivationDimension(BaseModel):
    dep_3_pct: Optional[float] = None
    dep_4_pct: Optional[float] = None
    dep_3_count: Optional[int] = None
    dep_4_count: Optional[int] = None
    unfiltered_dep_3_pct: float
    unfiltered_dep_4_pct: float
    min_dep_3_pct: float
    max_dep_3_pct: float
    min_dep_4_pct: float
    max_dep_4_pct: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            dep_3_pct=obj.dep_3_pct,
            dep_4_pct=obj.dep_4_pct,
            dep_3_count=obj.dep_3_count,
            dep_4_count=obj.dep_4_count,
            unfiltered_dep_3_pct=obj.unfiltered_dep_3_pct,
            unfiltered_dep_4_pct=obj.unfiltered_dep_4_pct,
            min_dep_3_pct=obj.min_dep_3_pct,
            max_dep_3_pct=obj.max_dep_3_pct,
            min_dep_4_pct=obj.min_dep_4_pct,
            max_dep_4_pct=obj.max_dep_4_pct,
        )


class AverageDailySunlightHoursPerArea(BaseModel):
    area_name: str
    average_daily_sunlight_hours: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            area_name=obj.area_name,
            average_daily_sunlight_hours=obj.average_daily_sunlight_hours
        )


class BuildingAttributePercentage(BaseModel):
    label: str
    value: float


class BuildingAttributePercentagesPerRegion(BaseModel):
    region_name: str
    attributes: List[BuildingAttributePercentage]


class BuildingWindDrivenRainSchema(BaseModel):
    wdr20_0: float
    wdr20_45: float
    wdr20_90: float
    wdr20_135: float
    wdr20_180: float
    wdr20_225: float
    wdr20_270: float
    wdr20_315: float

    wdr40_0: float
    wdr40_45: float
    wdr40_90: float
    wdr40_135: float
    wdr40_180: float
    wdr40_225: float
    wdr40_270: float
    wdr40_315: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            wdr20_0=obj.wdr20_0,
            wdr20_45=obj.wdr20_45,
            wdr20_90=obj.wdr20_90,
            wdr20_135=obj.wdr20_135,
            wdr20_180=obj.wdr20_180,
            wdr20_225=obj.wdr20_225,
            wdr20_270=obj.wdr20_270,
            wdr20_315=obj.wdr20_315,
            wdr40_0=obj.wdr40_0,
            wdr40_45=obj.wdr40_45,
            wdr40_90=obj.wdr40_90,
            wdr40_135=obj.wdr40_135,
            wdr40_180=obj.wdr40_180,
            wdr40_225=obj.wdr40_225,
            wdr40_270=obj.wdr40_270,
            wdr40_315=obj.wdr40_315,
        )


class BuildingWindDrivenRainData(BaseModel):
    north_two_degrees_median: float
    east_two_degrees_median: float
    south_east_two_degrees_median: float
    south_two_degrees_median: float
    south_west_two_degrees_median: float
    west_two_degrees_median: float
    north_west_two_degrees_median: float
    north_east_two_degrees_median: float

    north_four_degrees_median: float
    east_four_degrees_median: float
    south_east_four_degrees_median: float
    south_four_degrees_median: float
    south_west_four_degrees_median: float
    west_four_degrees_median: float
    north_west_four_degrees_median: float
    north_east_four_degrees_median: float


class BuildingHotSummerDaysSchema(BaseModel):
    hsd_baseline_01_20_median: float
    hsd_15_median: float
    hsd_20_median: float
    hsd_25_median: float
    hsd_30_median: float
    hsd_40_median: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            hsd_baseline_01_20_median=obj.hsd_baseline_01_20_median,
            hsd_15_median=obj.hsd_15_median,
            hsd_20_median=obj.hsd_20_median,
            hsd_25_median=obj.hsd_25_median,
            hsd_30_median=obj.hsd_30_median,
            hsd_40_median=obj.hsd_40_median,
        )


class BuildingHotSummerDaysData(BaseModel):
    hsd_baseline: float
    hsd_1_5_degree_above_baseline: float
    hsd_2_0_degree_above_baseline: float
    hsd_2_5_degree_above_baseline: float
    hsd_3_0_degree_above_baseline: float
    hsd_4_0_degree_above_baseline: float


class BuildingIcingDaysSchema(BaseModel):
    icingdays: float

    @classmethod
    def from_orm(cls, obj):
        return cls(icingdays=obj.icingdays)


class BuildingIcingDaysData(BaseModel):
    icing_days: float


class BuildingSunlightHoursSchema(BaseModel):
    sunlight_hours: float
    daily_sunlight_hours: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            sunlight_hours=obj.sunlight_hours,
            daily_sunlight_hours=obj.daily_sunlight_hours,
        )


class BuildingSunlightHoursData(BaseModel):
    sunlight_hours: float
    daily_sunlight_hours: float


class BuildingExtremeWeatherSummarySchema(BaseModel):
    affected_by_icing_days: Optional[bool] = None
    affected_by_hsds: Optional[bool] = None
    affected_by_wdr: Optional[bool] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            affected_by_icing_days=obj.affected_by_icing_days,
            affected_by_hsds=obj.affected_by_hsds,
            affected_by_wdr=obj.affected_by_wdr,
        )


class BuildingExtremeWeatherSummaryData(BaseModel):
    affected_by_icing_days: bool
    affected_by_hot_summer_days: bool
    affected_by_wind_driven_rain: bool


class BuildingDetailsForBulkDownloadSchema(BaseModel):
    uprn: str
    toid: Optional[str] = None
    first_line_of_address: Optional[str] = None
    post_code: Optional[str] = None
    longitude: float
    lattitude: float
    epc_rating: Optional[str] = None
    sap_rating: Optional[float] = None
    lodgement_date: Optional[datetime.date] = None
    sap_rating: Optional[int] = None
    type: Optional[str] = None
    built_form: Optional[str] = None
    fuel_type: Optional[str] = None
    floor_construction: Optional[str] = None
    floor_insulation: Optional[str] = None
    roof_construction: Optional[str] = None
    roof_insulation: Optional[str] = None
    roof_insulation_thickness: Optional[str] = None
    wall_construction: Optional[str] = None
    wall_insulation: Optional[str] = None
    window_glazing: Optional[str] = None
    roof_material: Optional[str] = None
    solar_panel_presence: Optional[str] = None
    roof_shape: Optional[str] = None
    roof_aspect_area_facing_north_m2: Optional[float] = None
    roof_aspect_area_facing_north_east_m2: Optional[float] = None
    roof_aspect_area_facing_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_m2: Optional[float] = None
    roof_aspect_area_facing_south_west_m2: Optional[float] = None
    roof_aspect_area_facing_west_m2: Optional[float] = None
    roof_aspect_area_facing_north_west_m2: Optional[float] = None
    roof_aspect_area_indeterminable_m2: Optional[float] = None
    wdr20_0: float
    wdr20_45: float
    wdr20_90: float
    wdr20_135: float
    wdr20_180: float
    wdr20_225: float
    wdr20_270: float
    wdr20_315: float
    wdr40_0: float
    wdr40_45: float
    wdr40_90: float
    wdr40_135: float
    wdr40_180: float
    wdr40_225: float
    wdr40_270: float
    wdr40_315: float
    hsd_baseline_01_20_median: float
    hsd_15_median: float
    hsd_20_median: float
    hsd_25_median: float
    hsd_30_median: float
    hsd_40_median: float
    icingdays: float
    sunlight_hours: float
    daily_sunlight_hours: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            uprn=obj.uprn,
            toid=obj.toid,
            first_line_of_address=obj.first_line_of_address,
            post_code=obj.post_code,
            longitude=obj.longitude,
            lattitude=obj.lattitude,
            epc_rating=obj.epc_rating,
            lodgement_date=obj.lodgement_date,
            sap_rating=obj.sap_rating,
            expiry_date=obj.expiry_date,
            type=obj.type,
            built_form=obj.built_form,
            fuel_type=obj.fuel_type,
            floor_construction=obj.floor_construction,
            floor_insulation=obj.floor_insulation,
            roof_construction=obj.roof_construction,
            roof_insulation=obj.roof_insulation,
            roof_insulation_thickness=obj.roof_insulation_thickness,
            wall_construction=obj.wall_construction,
            wall_insulation=obj.wall_insulation,
            window_glazing=obj.window_glazing,
            solar_panel_presence=str(obj.has_roof_solar_panels),
            roof_material=obj.roof_material,
            roof_shape=obj.roof_shape,
            roof_aspect_area_facing_north_m2=get_nullable_float(
                obj.roof_aspect_area_facing_north_m2
            ),
            roof_aspect_area_facing_north_east_m2=get_nullable_float(
                obj.roof_aspect_area_facing_north_east_m2
            ),
            roof_aspect_area_facing_east_m2=get_nullable_float(
                obj.roof_aspect_area_facing_east_m2
            ),
            roof_aspect_area_facing_south_east_m2=get_nullable_float(
                obj.roof_aspect_area_facing_south_east_m2
            ),
            roof_aspect_area_facing_south_m2=get_nullable_float(
                obj.roof_aspect_area_facing_south_m2
            ),
            roof_aspect_area_facing_south_west_m2=get_nullable_float(
                obj.roof_aspect_area_facing_south_west_m2
            ),
            roof_aspect_area_facing_west_m2=get_nullable_float(
                obj.roof_aspect_area_facing_west_m2
            ),
            roof_aspect_area_facing_north_west_m2=get_nullable_float(
                obj.roof_aspect_area_facing_north_west_m2
            ),
            roof_aspect_area_indeterminable_m2=get_nullable_float(
                obj.roof_aspect_area_indeterminable_m2
            ),
            wdr20_0=obj.wdr20_0,
            wdr20_45=obj.wdr20_45,
            wdr20_90=obj.wdr20_90,
            wdr20_135=obj.wdr20_135,
            wdr20_180=obj.wdr20_180,
            wdr20_225=obj.wdr20_225,
            wdr20_270=obj.wdr20_270,
            wdr20_315=obj.wdr20_315,
            wdr40_0=obj.wdr40_0,
            wdr40_45=obj.wdr40_45,
            wdr40_90=obj.wdr40_90,
            wdr40_135=obj.wdr40_135,
            wdr40_180=obj.wdr40_180,
            wdr40_225=obj.wdr40_225,
            wdr40_270=obj.wdr40_270,
            wdr40_315=obj.wdr40_315,
            hsd_baseline_01_20_median=obj.hsd_baseline_01_20_median,
            hsd_15_median=obj.hsd_15_median,
            hsd_20_median=obj.hsd_20_median,
            hsd_25_median=obj.hsd_25_median,
            hsd_30_median=obj.hsd_30_median,
            hsd_40_median=obj.hsd_40_median,
            icingdays=obj.icingdays,
            sunlight_hours=obj.sunlight_hours,
            daily_sunlight_hours=obj.daily_sunlight_hours,
        )


class BuildingDetailsForBulkDownload(BaseModel):
    uprn: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    first_line_of_address: Optional[str] = None
    post_code: Optional[str] = None
    energy_rating: Optional[str] = None
    sap_rating: Optional[float] = None
    toid: Optional[str] = None
    lodgement_date: Optional[datetime.date] = None
    built_form: Optional[str] = None
    floor_construction: Optional[str] = None
    floor_insulation: Optional[str] = None
    roof_construction: Optional[str] = None
    roof_insulation_location: Optional[str] = None
    roof_insulation_thickness: Optional[str] = None
    wall_construction: Optional[str] = None
    wall_insulation: Optional[str] = None
    window_glazing: Optional[str] = None
    fueltype: Optional[str] = None
    roof_material: Optional[str] = None
    solar_panel_presence: Optional[str] = None
    roof_shape: Optional[str] = None
    roof_aspect_area_facing_north_m2: Optional[float] = None
    roof_aspect_area_facing_north_east_m2: Optional[float] = None
    roof_aspect_area_facing_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_east_m2: Optional[float] = None
    roof_aspect_area_facing_south_m2: Optional[float] = None
    roof_aspect_area_facing_south_west_m2: Optional[float] = None
    roof_aspect_area_facing_west_m2: Optional[float] = None
    roof_aspect_area_facing_north_west_m2: Optional[float] = None
    roof_aspect_area_indeterminable_m2: Optional[float] = None
    north_two_degrees_median: float
    east_two_degrees_median: float
    south_east_two_degrees_median: float
    south_two_degrees_median: float
    south_west_two_degrees_median: float
    west_two_degrees_median: float
    north_west_two_degrees_median: float
    north_east_two_degrees_median: float
    north_four_degrees_median: float
    east_four_degrees_median: float
    south_east_four_degrees_median: float
    south_four_degrees_median: float
    south_west_four_degrees_median: float
    west_four_degrees_median: float
    north_west_four_degrees_median: float
    north_east_four_degrees_median: float
    hsd_baseline: float
    hsd_1_5_degree_above_baseline: float
    hsd_2_0_degree_above_baseline: float
    hsd_2_5_degree_above_baseline: float
    hsd_3_0_degree_above_baseline: float
    hsd_4_0_degree_above_baseline: float
    icing_days: float
    sunlight_hours: float
    daily_sunlight_hours: float
