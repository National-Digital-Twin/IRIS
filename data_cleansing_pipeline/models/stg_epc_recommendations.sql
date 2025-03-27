{{ config(materialized = 'table') }}
SELECT
    lmk_key,
    improvement_item,
    improvement_summary_text,
    improvement_descr_text,
    improvement_id,
    improvement_id_text,
    indicative_cost
FROM
    {{ source('postgres', 'recommendations') }}
