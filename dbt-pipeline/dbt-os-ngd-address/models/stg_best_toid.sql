-- models/int/int_uprn_best_toid.sql

with src as (

    select
        "IDENTIFIER_1" as uprn,
        "IDENTIFIER_2" as toid,
        "VERSION_DATE_1" as version_date_1,
        "VERSION_DATE_2" as version_date_2,
        "VERSION_NUMBER_1" as version_number_1,
        "VERSION_NUMBER_2" as version_number_2,
        "CONFIDENCE" as confidence
    from {{ source('postgres', 'uprn_toid') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by uprn
            order by
                case confidence
                    when 'Version information is correct' then 3
                    when 'Version information has potentially changed' then 2
                    when 'Version information has changed' then 1
                    else 0
                end desc,
                version_date_1 desc nulls last,
                version_date_2 desc nulls last,
                version_number_1 desc nulls last,
                version_number_2 desc nulls last,
                toid asc
        ) as rn
    from src

)

select
    uprn,
    toid,
    confidence,
    version_date_1,
    version_date_2,
    version_number_1,
    version_number_2
from ranked
where rn = 1
