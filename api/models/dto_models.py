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
    lodgement_date: Optional[str] = None
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
    epc_rating: Optional[str]
    structure_unit_type: Optional[str]

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
    built_form: Optional[str]
    lodgement_date: Optional[datetime.date]
    fuel_type: Optional[str]
    window_glazing: Optional[str]
    wall_construction: Optional[str]
    wall_insulation: Optional[str]
    floor_construction: Optional[str]
    floor_insulation: Optional[str]
    has_roof_solar_panels: Optional[bool]
    roof_material: Optional[str]
    roof_aspect_area_facing_north_m2: Optional[float]
    roof_aspect_area_facing_north_east_m2: Optional[float]
    roof_aspect_area_facing_east_m2: Optional[float]
    roof_aspect_area_facing_south_east_m2: Optional[float]
    roof_aspect_area_facing_south_m2: Optional[float]
    roof_aspect_area_facing_south_west_m2: Optional[float]
    roof_aspect_area_facing_west_m2: Optional[float]
    roof_aspect_area_facing_north_west_m2: Optional[float]
    roof_construction: Optional[str]
    roof_insulation: Optional[str]
    roof_insulation_thickness: Optional[str]

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


class PercentageBuildingAttributesPerRegion(BaseModel):
    region_name: str
    percentage_roof_solar_panels: float
    percentage_double_glazing: float
    percentage_single_glazing: float
    percentage_solid_floor: float
    percentage_roof_insulation_thickness_150mm: float
    percentage_roof_insulation_thickness_200mm: float
    percentage_roof_insulation_thickness_250mm: float
    percentage_pitched_roof: float
    percentage_cavity_wall: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            region_name=obj.region_name,
            percentage_roof_solar_panels=obj.percentage_roof_solar_panels,
            percentage_double_glazing=obj.percentage_double_glazing,
            percentage_single_glazing=obj.percentage_single_glazing,
            percentage_solid_floor=obj.percentage_solid_floor,
            percentage_roof_insulation_thickness_150mm=obj.percentage_roof_insulation_thickness_150mm,
            percentage_roof_insulation_thickness_200mm=obj.percentage_roof_insulation_thickness_200mm,
            percentage_roof_insulation_thickness_250mm=obj.percentage_roof_insulation_thickness_250mm,
            percentage_pitched_roof=obj.percentage_pitched_roof,
            percentage_cavity_wall=obj.percentage_cavity_wall,
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
    filtered_avg_sap_rating: Optional[float]

    @classmethod
    def from_orm(cls, obj):
        return cls(
            date=obj.date,
            national_avg_sap_rating=obj.national_avg_sap_rating,
            filtered_avg_sap_rating=obj.filtered_avg_sap_rating,
        )


class BuildingsAffectedByExtremeWeather(BaseModel):
    number_of_buildings: int
    affected_by_icing_days: Optional[bool]
    affected_by_hsds: Optional[bool]
    affected_by_wdr: Optional[bool]

    @classmethod
    def from_orm(cls, obj):
        return cls(
            number_of_buildings=obj.number_of_buildings,
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
