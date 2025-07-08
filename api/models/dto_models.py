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
        )


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
    roof_construction: set[str] = set()
    roof_insulation_location: set[str] = set()
    roof_insulation_thickness: set[str] = set()
