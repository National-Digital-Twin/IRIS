{{ config(materialized='table') }}

-- Final address profiling mart built from the deduped EPC features.

with src as (
    select * from {{ ref('int_epc_no_uprn_address_dedup') }}
)

select
    lmk_key as "LMK_KEY",
    uprn as "UPRN",
    match_score as "MatchScore",
    concat_ws(', ', initcap(address), initcap(posttown), upper(postcode)) as "Address",
    upper(postcode) as "Postcode",
    environmental_impact_rating as "EnvironmentalImpactRating",
    tco2 as "tCO2",
    heating_cost_gbp_per_yr as "HeatingCost(£/yr)",
    saprating as "SAPRating",
    sapband as "SAPBand",
    lodgement_date as "LodgementDate",
    property_type as "PropertyType",
    construction_age_band as "ConstructionAgeBand",
    built_form as "BuiltForm",
    main_heating_category as "MainHeatingCategory",
    main_fuel_type as "MainFuelType",
    roof_construction as "RoofConstruction",
    roof_insulation_location as "RoofInsulationLocation",
    roof_insulation_thickness as "RoofInsulationThickness",
    wall_construction as "WallConstruction",
    wall_insulation_type as "WallInsulationType",
    floor_construction as "FloorConstruction",
    floor_insulation as "FloorInsulation",
    multiple_glazing_type as "MultipleGlazingType",
    open_fireplaces_count as "OpenFireplacesCount",
    renewables as "Renewables",
    ventilation as "Ventilation",
    water_heating_cost_gbp_per_yr as "WaterHeatingCost(£/yr)",
    lighting_cost_gbp_per_yr as "LightingCost(£/yr)",
    total_floor_area as "TotalFloorArea",
    certificate_type as "CertificateType"
from src
