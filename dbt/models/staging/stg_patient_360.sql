{{ config(materialized='view') }}

select
    patient_id,
    first_name,
    last_name,
    gender,
    birth_date,
    city,
    state,
    diabetes_status,
    hypertension_status,
    latest_hba1c_date,
    latest_hba1c_value,
    latest_hba1c_unit,
    days_since_hba1c,
    hba1c_care_gap,
    latest_bp_date,
    systolic_bp,
    diastolic_bp,
    days_since_bp,
    bp_care_gap,
    total_encounters,
    last_encounter_date,
    analysis_date
from workspace.default.gold_patient_360
