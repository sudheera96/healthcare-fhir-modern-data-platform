{{ config(materialized='view') }}

select
    patient_id,
    first_name,
    last_name,
    gender,
    birth_date,
    city,
    state,
    latest_hba1c_date,
    latest_hba1c_value,
    latest_hba1c_unit,
    days_since_hba1c,
    hba1c_care_gap,
    analysis_date
from workspace.default.gold_diabetes_care_gap
