{{ config(materialized='view') }}

select
    p.patient_id,
    p.first_name,
    p.last_name,
    p.gender,
    p.birth_date,
    p.city,
    p.state,

    d.latest_hba1c_date,
    d.latest_hba1c_value,
    d.latest_hba1c_unit,
    d.days_since_hba1c,
    d.hba1c_care_gap,

    h.latest_bp_date,
    h.systolic_bp,
    h.diastolic_bp,
    h.days_since_bp,
    h.bp_care_gap,

    case
        when d.hba1c_care_gap = 'care_gap'
             and h.bp_care_gap = 'care_gap'
            then 'diabetes_and_hypertension'
        when d.hba1c_care_gap = 'care_gap'
            then 'diabetes'
        when h.bp_care_gap = 'care_gap'
            then 'hypertension'
        else 'none'
    end as care_gap_type,

    p.total_encounters,
    p.last_encounter_date,
    p.analysis_date

from {{ ref('stg_patient_360') }} p

left join {{ ref('stg_diabetes_care_gap') }} d
    on p.patient_id = d.patient_id

left join {{ ref('stg_hypertension_care_gap') }} h
    on p.patient_id = h.patient_id
