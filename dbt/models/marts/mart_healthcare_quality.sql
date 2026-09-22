{{ config(materialized='table') }}

select
    analysis_date,

    count(*) as total_patients,

    count_if(hba1c_care_gap is not null) as diabetes_patients,

    count_if(bp_care_gap is not null) as hypertension_patients,

    count_if(hba1c_care_gap = 'care_gap') as diabetes_care_gap_patients,

    count_if(bp_care_gap = 'care_gap') as hypertension_care_gap_patients,

    count_if(
        care_gap_type = 'diabetes_and_hypertension'
    ) as patients_with_both_care_gaps,

    count_if(
        care_gap_type != 'none'
    ) as patients_with_any_care_gap,

    round(
        count_if(care_gap_type != 'none') * 100.0 / count(*),
        2
    ) as overall_care_gap_rate

from {{ ref('int_patient_care_gaps') }}

group by analysis_date
