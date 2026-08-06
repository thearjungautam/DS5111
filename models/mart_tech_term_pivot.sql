{{ config(materialized='table') }}

{% set core_terms = ['python', 'sql', 'dbt', 'snowflake', 'aws', 'docker'] %}

SELECT
    VIDEO_ID,

    {% for term in core_terms %}

    SUM(
        CASE
            WHEN LOWER(TERM_NAME) = '{{ term }}' THEN 1
            ELSE 0
        END
    ) AS COUNT_{{ term | upper }}_MENTIONS

    {% if not loop.last %},{% endif %}

    {% endfor %}

FROM {{ ref('fct_tech_terms') }}
GROUP BY VIDEO_ID
