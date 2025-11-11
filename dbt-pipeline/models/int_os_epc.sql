{{ config(materialized='table') }}
SELECT
    epc.uprn,
    os.udprn,
    '' AS "AddressId",
    epc.address AS "Address",
    CAST(epc.current_energy_efficiency AS NUMERIC) AS "SAP",
    CAST(epc.environment_impact_current AS NUMERIC) AS "EI",
    CAST(0 AS NUMERIC) AS "KgCO2SAP2012",
    CAST(0 AS NUMERIC) AS "KgCO22017",
    CAST(0 AS NUMERIC) AS "KgCO2SAP102",
    CAST(0 AS NUMERIC) AS "KgCO22025",
    CAST(0 AS NUMERIC) AS "KgCO22030",
    CAST(0 AS NUMERIC) AS "KgCO22038",
    CAST(0 AS NUMERIC) AS "KgCO22050",
    CAST(0 AS NUMERIC) AS "FuelBills",
    CAST(0 AS NUMERIC) AS "FuelBillsRealistic",
    CAST(0 AS NUMERIC) AS "HeatingCost",
    CAST(0 AS NUMERIC) AS "kWhyr",
    CAST(0 AS NUMERIC) AS "kWhHeatingDemandm2yr",
    CAST(0 AS NUMERIC) AS "AvHeatLossCoefficientwK",
    CAST(0 AS NUMERIC) AS "TotalFloorArea",
    rec.improvement_item AS "ImprovementIndex",
    rec.improvement_summary_text AS "Category",
    rec.improvement_id AS "MeasureGroupId",
    rec.improvement_id_text AS "MeasureGroupName",
    rec.indicative_cost AS "COST",
    rec.improvement_descr_text AS "ImprovementDescrText",
    CAST(0 AS NUMERIC) AS "CumulativeCost",
    CAST(0 AS NUMERIC) AS "SAPfollowingthisMeasure",
    CAST(0 AS NUMERIC) AS "IndividualSAPincrease",
    CAST(0 AS NUMERIC) AS "CumulativeSAPincrease",
    CAST(0 AS NUMERIC) AS "AverageHeatLossCoefficient (w/K)",
    rec.improvement_id AS "MeasureOutcomeId",
    rec.improvement_id_text AS "MeasureOutcomeName",
    epc.fuzzy_matched AS "FuzzyMatched"
FROM {{ ref("int_epc_certificates") }} AS epc
LEFT JOIN {{ ref("stg_epc_recommendations") }} AS rec
    ON epc.lmk_key = rec.lmk_key
LEFT JOIN {{ ref("stg_os_places") }} AS os
    ON epc.uprn = os.uprn AND os.os_api_source = 'DPA'
