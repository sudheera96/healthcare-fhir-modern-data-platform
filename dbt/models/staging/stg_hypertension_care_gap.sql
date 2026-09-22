{{ config(materialized='view') }}

select
    patient_id,
    first_name,
    last_name,
    gender,
    birth_date,
    city,
    state,
    latest_bp_date,
    systolic_bp,
    diastolic_bp,
    days_since_bp,
    bp_care_gap,
    analysis_date
from workspace.default.gold_hypertension_care_gap
