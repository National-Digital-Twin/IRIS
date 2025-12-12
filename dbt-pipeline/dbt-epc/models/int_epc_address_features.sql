{{ config(materialized='view') }}

-- Map raw split fields into normalized feature columns.

select
    lmk_key,
    uprn,
    address,
    postcode,
    current_energy_efficiency as saprating,
    current_energy_rating as sapband,
    lodgement_date,
    trim(regexp_replace(construction_age_band, '^\s*England and Wales:\s*', '', 'i')) as construction_age_band,
    nullif(regexp_replace(initcap(built_form), '[^A-Za-z0-9]', '', 'g'), '') as built_form,
    total_floor_area,
    environment_impact_current as environmental_impact_rating,
    co2_emissions_current as tco2,
    heating_cost_current as heating_cost_gbp_per_yr,
    hot_water_cost_current as water_heating_cost_gbp_per_yr,
    lighting_cost_current as lighting_cost_gbp_per_yr,
    property_type,
    posttown,
    -- heating category (aligned with original Python mapping)
    case
        when lower(mainheat_description) like '%boiler and radiators, mains gas%' then 'BoilerRadiatorsMainsGas'
        when lower(mainheat_description) like '%electric storage heaters%' or lower(mainheat_description) like '%portable electric heaters%' then 'ElectricHeaters'
        when lower(mainheat_description) like '%boiler and radiators, lpg%' or lower(mainheat_description) like '%boiler and underfloor heating, lpg%' then 'BoilerRadiatorsLPG'
        when lower(mainheat_description) like '%boiler and radiators, oil%' or lower(mainheat_description) like '%boiler and underfloor heating, oil%' then 'BoilerRadiatorsOil'
        when lower(mainheat_description) like '%electric underfloor heating%' then 'ElectricUnderfloor'
        when lower(mainheat_description) like '%community scheme%' then 'CommunityScheme'
        when lower(mainheat_description) like '%warm air, mains gas%' then 'WarmAirMainsGas'
        when lower(mainheat_description) like '%boiler & underfloor, mains gas%' or lower(mainheat_description) like '%boiler and underfloor heating, mains gas%' then 'BoilerUnderfloorMainsGas'
        when lower(mainheat_description) like '%air source heat pump%' then 'AirSourceHeatPump'
        when lower(mainheat_description) like '%boiler and radiators, electric%' or lower(mainheat_description) like '%boiler and underfloor heating, electric%' then 'BoilerRadiatorsElectric'
        when lower(mainheat_description) like '%ground source heat pump%' then 'GroundSourceHeatPump'
        when lower(mainheat_description) like '%boiler and radiators, dual fuel%' then 'BoilerRadiatorsDualFuel'
        when lower(mainheat_description) like '%boiler and radiators, wood%' then 'BoilerRadiatorsWood'
        when lower(mainheat_description) like '%room heaters, mains gas%' then 'RoomHeatersMainsGas'
        when lower(mainheat_description) like '%no system present%' then 'NoSystemPresent'
        when lower(mainheat_description) like '%water source heat pump%' then 'WaterSourceHeatPump'
        else 'Other'
    end as main_heating_category,
    -- fuel category mapped to final fuel_type_map targets
    case
        when main_fuel ilike '%mains gas%' then 'NaturalFuelGas'
        when main_fuel ilike '%electricity%' or main_fuel ilike '%electric%' then 'Electricity'
        when main_fuel ilike '%oil%' then 'Oil'
        when main_fuel ilike '%lpg%' then 'LPG'
        when main_fuel ilike '%dual fuel%' then 'Fuel'
        when main_fuel ilike '%wood logs%' then 'WoodLogs'
        when main_fuel ilike '%wood pellets%' then 'WoodPellets'
        when main_fuel ilike '%wood chips%' then 'WoodChips'
        when main_fuel ilike '%house coal%' then 'Coal'
        when main_fuel ilike '%anthracite%' then 'Anthracite'
        when main_fuel ilike '%smokeless coal%' then 'SmokelessCoal'
        when main_fuel ilike '%biomass%' then 'Biomass'
        when main_fuel ilike '%biogas%' then 'Fuel'
        when main_fuel ilike '%no heating/hot-water system%' then 'Fuel'
        when main_fuel ilike '%invalid%' then 'Fuel'
        else 'Fuel'
    end as main_fuel_type,
    -- glazing
    case
        when glazed_type ilike '%double%' and glazed_type ilike '%before%2002%' then 'DoubleGlazingBefore2002'
        when glazed_type ilike '%double%' and glazed_type ilike '%2002%' then 'DoubleGlazingAfter2002'
        when glazed_type ilike '%double%' then 'DoubleGlazing'
        when glazed_type ilike '%triple%' then 'TripleGlazing'
        when glazed_type ilike '%secondary%' then 'SecondaryGlazing'
        when glazed_type ilike '%single%' then 'SingleGlazing'
        else null
    end as multiple_glazing_type,
    -- roof mappings
    case
        when roof_construction_raw ilike '%pitched%' then 'Pitched'
        when roof_construction_raw ilike '%roof room%' then 'RoofRoom'
        when roof_construction_raw ilike '%flat%' then 'Flat'
        when roof_construction_raw ilike '%other premises above%' then 'OtherPremisesAbove'
        when roof_construction_raw ilike '%another dwelling above%' then 'AnotherDwellingAbove'
        when roof_construction_raw ilike '%thatched%' then 'Thatched'
        else null
    end as roof_construction,
    case
        when roof_insulation_raw ilike '%mm%' then regexp_replace(roof_insulation_raw, '[^0-9+]', '', 'g') || 'mm'
        else null
    end as roof_insulation_thickness,
    case
        when roof_insulation_raw is null or trim(roof_insulation_raw) = '' then null
        when roof_insulation_raw ilike '%rafters%' then 'InsulatedAtRafters'
        when roof_insulation_raw ilike '%ceiling insulated%' then 'CeilingInsulated'
        when roof_insulation_raw ilike '%flat roof%' then 'FlatRoofInsulation'
        when roof_insulation_raw ilike '%with additional insulation%' then 'ThatchedWithAdditionalInsulation'
        when roof_insulation_raw ilike '%thatched%' then 'InsulatedWithThatched'
        when roof_insulation_raw ilike '%limited insulation%' and roof_insulation_raw ilike '%assumed%' then 'LimitedInsulationAssumed'
        when roof_insulation_raw ilike '%limited insulation%' then 'LimitedInsulation'
        when roof_insulation_raw ilike '%insulated%' and roof_insulation_raw ilike '%assumed%' then 'InsulatedAssumed'
        when roof_insulation_raw ilike '%insulated%' then 'Insulated'
        when roof_insulation_raw ilike '%loft insulation%' and roof_insulation_raw ilike '%assumed%' then 'LoftInsulationAssumed'
        when roof_insulation_raw ilike '%loft insulation%' then 'LoftInsulation'
        when roof_insulation_raw ilike '%no insulation%' and roof_insulation_raw ilike '%assumed%' then 'NoInsulationAssumedInRoof'
        when roof_insulation_raw ilike '%no insulation%' then 'NoInsulationInRoof'
        when roof_insulation_raw ilike '%unknown%' then null
        else nullif(trim(roof_insulation_extra), '')
    end as roof_insulation_location,
    -- wall mappings (aligned to original Python transform_wall_construction)
    case
        when wall_construction_raw ilike '%cavity wall%' then 'CavityWall'
        when wall_construction_raw ilike '%timber frame%' then 'TimberFrame'
        when wall_construction_raw ilike '%solid brick%' then 'SolidBrick'
        when wall_construction_raw ilike '%sandstone or limestone%' then 'SandstoneOrLimestone'
        when wall_construction_raw ilike '%sandstone%' then 'Sandstone'
        when wall_construction_raw ilike '%granite%' or wall_construction_raw ilike '%whin%' then 'GraniteOrWhinstone'
        when wall_construction_raw ilike '%park home wall%' then 'ParkHomeWall'
        when wall_construction_raw ilike '%cob%' then 'Cob'
        when wall_construction_raw ilike '%system built%' then 'SystemBuilt'
        else 'Other'
    end as wall_construction,
    case
        when wall_insulation_raw ilike '%filled cavity%' and wall_insulation_raw ilike '%internal%' then 'InternalInsulation'
        when wall_insulation_raw ilike '%filled cavity%' and wall_insulation_raw ilike '%external%' then 'ExternalInsulation'
        when wall_insulation_raw ilike '%filled cavity%' then 'InsulatedWall'
        when wall_insulation_raw ilike '%internal%' then 'InternalInsulation'
        when wall_insulation_raw ilike '%external%' then 'ExternalInsulation'
        when wall_insulation_raw ilike '%additional insulation%' then 'InsulatedWall'
        when wall_insulation_raw ilike '%as built%' then 'InsulatedWall'
        when wall_insulation_raw ilike '%partial%' then 'PartialInsulation'
        when wall_insulation_raw is null or trim(wall_insulation_raw) = '' then 'NoInsulationInWall'
        else 'WallInsulation'
    end as wall_insulation_type,
    -- floor mappings
    case
        when floor_construction_raw ilike '%solid%' then 'Solid'
        when floor_construction_raw ilike '%suspended%' then 'Suspended'
        when floor_construction_raw ilike '%another dwelling above%' then 'AnotherDwellingAbove'
        when floor_construction_raw ilike '%another dwelling below%' then 'AnotherDwellingBelow'
        else null
    end as floor_construction,
    case
        when floor_insulation_raw ilike '%no insulation%' or floor_insulation_raw ilike '%uninsulated%' then 'NoInsulationInFloor'
        when floor_insulation_raw ilike '%limited%' then 'LimitedFloorInsulation'
        when floor_insulation_raw is null or trim(floor_insulation_raw) = '' then null
        else 'InsulatedFloor'
    end as floor_insulation,
    windows_description,
    floor_description,
    number_open_fireplaces as open_fireplaces_count,
    wind_turbine_count as renewables,
    case
        when mechanical_ventilation ilike '%mechanical supply and extract%' then 'MechanicalSupplyAndExtract'
        when mechanical_ventilation ilike '%mechanical%' and mechanical_ventilation ilike '%supply%' and mechanical_ventilation ilike '%extract%' then 'MechanicalSupplyAndExtract'
        when mechanical_ventilation ilike '%mechanical ventilation%' then 'MechanicalSupplyAndExtract'
        when mechanical_ventilation ilike '%mechanical extract%' then 'MechanicalExtractOnly'
        when mechanical_ventilation ilike '%mechanical%' then 'MechanicalExtractOnly'
        else 'NaturalVentilation'
    end as ventilation,
    certificate_type
from {{ ref('int_epc_address_split') }}
