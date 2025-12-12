{{ config(materialized = 'table') }}

(
SELECT
    osid,
    uprnreference,
    region,
    buildinguse,
    description,
    versiondate,
    roofmaterial_capturemethod,
    roofmaterial_confidenceindicator,
    roofmaterial_evidencedate,
    roofmaterial_greenroofpresence,
    roofmaterial_primarymaterial,
    roofmaterial_solarpanelpresence,
    roofmaterial_updatedate,
    roofshapeaspect_areafacingeast_m2,
    roofshapeaspect_areafacingnorth_m2,
    roofshapeaspect_areafacingnortheast_m2,
    roofshapeaspect_areafacingnorthwest_m2,
    roofshapeaspect_areafacingsouth_m2,
    roofshapeaspect_areafacingsoutheast_m2,
    roofshapeaspect_areafacingsouthwest_m2,
    roofshapeaspect_areafacingwest_m2,
    roofshapeaspect_areaflat_m2,
    roofshapeaspect_areaindeterminable_m2,
    roofshapeaspect_areapitched_m2,
    roofshapeaspect_areatotal_m2,
    roofshapeaspect_capturemethod,
    roofshapeaspect_confidenceindicator,
    roofshapeaspect_evidencedate,
    roofshapeaspect_shape,
    roofshapeaspect_updatedate
FROM {{ source('postgres', 'os_ngd_buildings_east_mids') }}
)
