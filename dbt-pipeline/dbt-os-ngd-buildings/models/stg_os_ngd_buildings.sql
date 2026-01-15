{{ config(materialized = 'table') }}

with buildings as 
    (
    SELECT
        osid,
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
    FROM {{ source('postgres', 'bld_fts_building') }}
    ),

    crossref as (
        select
            buildingid,
            jsonb_agg(
                distinct jsonb_build_object(
                    'uprn', uprn::bigint,
                    'buildingid', buildingid,
                    'buildingversiondate', buildingversiondate
                )
            ) filter (where uprn is not null) as uprnreference
        from {{ source('postgres', 'bld_fts_building_bldtoaddrcrossref')}}   -- your left-joined source, but ideally just the xref table
        group by buildingid
    )

select
    b.*,
    coalesce(c.uprnreference, '[]'::jsonb) as uprnreference
from buildings b
left join crossref c 
    on c.buildingid=b.osid
