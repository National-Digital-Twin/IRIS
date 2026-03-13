{{ config(materialized='table') }}

with os_ngd_address as (
    select
        cast(nullif(trim("uprn"), '') as text) as uprn,
        cast(nullif(trim("versiondate"), '') as date) as versiondate,
        cast(nullif(trim("versionavailablefromdate"), '') as timestamp) as versionavailablefromdate,
        cast(nullif(trim("versionavailabletodate"), '') as timestamp) as versionavailabletodate,
        nullif(trim("changetype"), '') as changetype,
        nullif(trim("theme"), '') as theme,
        nullif(trim("description"), '') as "description",
        nullif(trim("organisationname"), '') as organisationname,
        nullif(trim("poboxnumber"), '') as poboxnumber,
        nullif(trim("subname"), '') as subname,
        nullif(trim("name"), '') as "name",
        nullif(trim("number"), '') as "number",
        nullif(trim("streetname"), '') as streetname,
        nullif(trim("locality"), '') as locality,
        nullif(trim("townname"), '') as townname,
        nullif(trim("islandname"), '') as islandname,
        nullif(trim("postcode"), '') as postcode,
        nullif(trim("fulladdress"), '') as fulladdress,
        nullif(trim("country"), '') as country,
        nullif(trim("alternatelanguagesubname"), '') as alternatelanguagesubname,
        nullif(trim("alternatelanguagename"), '') as alternatelanguagename,
        nullif(trim("alternatelanguagenumber"), '') as alternatelanguagenumber,
        nullif(trim("alternatelanguagestreetname"), '') as alternatelanguagestreetname,
        nullif(trim("alternatelanguagelocality"), '') as alternatelanguagelocality,
        nullif(trim("alternatelanguagetownname"), '') as alternatelanguagetownname,
        nullif(trim("alternatelanguageislandname"), '') as alternatelanguageislandname,
        nullif(trim("alternatelanguage"), '') as alternatelanguage,
        nullif(trim("alternatelanguagefulladdress"), '') as alternatelanguagefulladdress,
        nullif(trim("floorlevel"), '') as floorlevel,
        cast(nullif(trim("lowestfloorlevel"), '') as numeric) as lowestfloorlevel,
        cast(nullif(trim("highestfloorlevel"), '') as numeric) as highestfloorlevel,
        nullif(trim("classificationcode"), '') as classificationcode,
        nullif(trim("classificationdescription"), '') as classificationdescription,
        nullif(trim("primaryclassificationdescription"), '') as primaryclassificationdescription,
        nullif(trim("secondaryclassificationdescription"), '') as secondaryclassificationdescription,
        nullif(trim("tertiaryclassificationdescription"), '') as tertiaryclassificationdescription,
        nullif(trim("quaternaryclassificationdescription"), '') as quaternaryclassificationdescription,
        nullif(trim("buildstatus"), '') as buildstatus,
        cast(nullif(trim("buildstatusdate"), '') as date) as buildstatusdate,
        nullif(trim("addressstatus"), '') as addressstatus,
        nullif(trim("postcodesource"), '') as postcodesource,
        cast(nullif(trim("parentuprn"), '') as text) as parentuprn,
        cast(nullif(trim("rootuprn"), '') as text) as rootuprn,
        cast(nullif(trim("hierarchylevel"), '') as integer) as hierarchylevel,
        cast(nullif(trim("usrn"), '') as bigint) as usrn,
        nullif(trim("usrnmatchindicator"), '') as usrnmatchindicator,
        nullif(trim("localcustodiancode"), '') as localcustodiancode,
        nullif(trim("localcustodiandescription"), '') as localcustodiandescription,
        nullif(trim("lowertierlocalauthoritygsscode"), '') as lowertierlocalauthoritygsscode,
        cast(nullif(trim("easting"), '') as numeric) as easting,
        cast(nullif(trim("northing"), '') as numeric) as northing,
        cast(nullif(trim("latitude"), '') as numeric) as latitude,
        cast(nullif(trim("longitude"), '') as numeric) as longitude,
        nullif(trim("geometry"), '') as "geometry",
        nullif(trim("positionalaccuracy"), '') as positionalaccuracy,
        cast(nullif(trim("effectivestartdate"), '') as date) as effectivestartdate,
        cast(nullif(trim("effectiveenddate"), '') as date) as effectiveenddate
    from {{ source('postgres', 'add_gb_build_addresses') }}
    ),

    best_toid as (
        select *
        from {{ ref('stg_best_toid') }}
    )

select 
    os_ngd_address.*,
    best_toid.toid as toid,
    best_toid.confidence as toid_confidence,
    best_toid.version_date_1 as toid_uprn_version_date,
    best_toid.version_date_2 as toid_feature_version_date
from os_ngd_address
left join best_toid
    on os_ngd_address.uprn=best_toid.uprn
