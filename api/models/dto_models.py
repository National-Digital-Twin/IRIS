# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from enum import Enum
from ianode_labels import IANodeSecurityLabelsV2, SecurityLabelBuilder
from pydantic import BaseModel
from typing import List, Optional
import pydantic

print(pydantic.VERSION)

from .ies_models import IesThing

def to_camel(field: str) -> str:
    if field.lower() == 'uprn' or field.lower() == 'toid':
        return field.upper()
    parts = field.split('_')
    return ''.join(word.capitalize() for word in parts[0:])

class AccessUser(BaseModel):
    username: str
    user_id: str
    active: Optional[bool] = None
    email: Optional[str] = None
    attributes: dict[str, str]
    groups: List[str]

class Building(IesThing):
    uprn: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    structure_unit_type: Optional[str] = None

class DetailedBuilding(Building):
    postcode: Optional[str] = None
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
        'alias_generator': to_camel,
        'populate_by_name': True,
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
        'alias_generator': to_camel,
        'populate_by_name': True,
    }


class SimpleBuilding(Building):
    first_line_of_address: Optional[str] = None
    energy_rating: Optional[str] = None
    toid: Optional[str] = None
