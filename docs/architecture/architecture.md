# Healthcare FHIR Modern Data Platform — Architecture

## 1. Overview

The platform transforms synthetic FHIR R4 healthcare data into validated, business-ready healthcare analytics.

The architecture separates source preservation, data engineering, business transformation, infrastructure management, and presentation.

## 2. End-to-End Flow

```text
Synthea / FHIR R4
        |
        v
Databricks Volume
        |
        v
Bronze
Raw FHIR + ingestion metadata
        |
        v
Silver
Parsed / standardized FHIR resources
        |
        +------------------+
        |                  |
        v                  v
   Data Quality       Quarantine
        |
      PASS
        |
        v
Gold
Healthcare business metrics
        |
        v
dbt
Staging → Intermediate → Marts
        |
        v
Databricks SQL Dashboard
```

## 3. Bronze Layer

Bronze preserves each source FHIR record as raw JSON while adding:

- source file
- ingestion timestamp
- resource type
- resource ID

This provides traceability and preserves the original representation before analytical transformation.

## 4. Silver Layer

Silver converts nested FHIR resources into analytical structures.

Implemented resources:

- Patient
- Condition
- Observation
- Encounter

Silver responsibilities include:

- FHIR reference parsing
- field extraction
- date normalization
- clinical-code extraction
- validation
- preparation for downstream analytics

## 5. Data Quality and Quarantine

Invalid relationships are not silently dropped.

For encounters:

```text
Encounter
   |
   v
Patient reference validation
   |
   +-- valid --> Silver / Gold
   |
   +-- invalid -> quarantine_encounter
```

The project identified 6,396 encounters without a usable patient reference and quarantined them.

## 6. Gold Layer

Gold contains business-oriented outputs:

- `gold_diabetes_care_gap`
- `gold_hypertension_care_gap`
- `gold_healthcare_quality_metrics`
- `gold_patient_360`

The Gold layer answers operational questions instead of exposing raw FHIR structures to dashboard users.

## 7. dbt Layer

dbt provides analytics engineering on top of the Databricks Gold layer.

### Staging

- `stg_patient_360`
- `stg_diabetes_care_gap`
- `stg_hypertension_care_gap`

### Intermediate

- `int_patient_care_gaps`

### Marts

- `mart_healthcare_quality`
- `mart_patient_care_gaps`

The final build completed with 18/18 resources passing.

## 8. Infrastructure

Terraform manages Databricks infrastructure configuration.

Current implementation includes:

- Databricks provider
- workspace catalog lookup
- `workspace.healthcare_analytics` schema

Terraform provides repeatable and reviewable infrastructure changes.

## 9. BI Layer

Databricks SQL Dashboard is the implemented presentation layer.

Dashboard components include:

- total patient KPI
- diabetes care gaps
- hypertension care gaps
- patients with any care gap
- care-gap rate by condition
- encounter data quality
- patient-level care-gap table

## 10. Security Boundary

The platform uses synthetic data and follows HIPAA-aligned design principles.

Sensitive identifiers unnecessary for analytics are not propagated into Silver or Gold.

See `../security/hipaa-aligned-security.md`.

## 11. External Platform Decisions

Snowflake was provisioned as an enterprise analytics target, but Delta Sharing could not be fully validated because the Snowflake Trial environment returned `DS_GATEKEEPER_DISABLED`.

Omni was evaluated but not implemented because the available signup path required work-email access.

The implemented architecture therefore uses Databricks SQL Dashboard.
