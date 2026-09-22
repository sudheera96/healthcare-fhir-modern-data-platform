# Data Ingestion, Quality, and Engineering Findings

## Purpose

This document records the important data problems, engineering
decisions, validation findings, and corrections encountered while
building the Healthcare FHIR Modern Data Platform.

The goal is to show that the project did not assume clean healthcare
data. The pipeline was designed to identify, investigate, and handle
real-world data-quality issues.

## 1. Source Data

Synthetic FHIR R4 data was generated with Synthea.

The generated dataset contained multiple FHIR resource types, including:

-   Patient
-   Encounter
-   Condition
-   Observation
-   DiagnosticReport
-   MedicationRequest
-   MedicationAdministration
-   Procedure
-   CarePlan
-   CareTeam
-   AllergyIntolerance
-   Immunization
-   Device
-   Claim
-   ExplanationOfBenefit
-   DocumentReference
-   ImagingStudy
-   Medication
-   SupplyDelivery
-   Provenance
-   Location
-   Organization
-   Practitioner
-   PractitionerRole

The raw dataset was several gigabytes in size.

Raw healthcare data was intentionally excluded from Git.

## 2. Bronze Ingestion Decision

FHIR NDJSON is nested and not immediately convenient for analytical SQL.

The Bronze design therefore preserved each FHIR record as:

-   `raw_json`
-   `source_file`
-   `ingestion_timestamp`
-   `resource_type`
-   `resource_id`

This preserves source traceability while creating queryable Delta
tables.

## 3. Patient Data Findings

The Patient resource contained synthetic identifiers and demographic
fields.

Validation found:

-   1,141 patient records
-   1,141 unique patient IDs
-   0 missing patient IDs
-   91 missing birth dates
-   91 missing gender values

### Engineering decision

Missing birth date and gender were retained as nulls rather than
inventing values.

This preserves source truth and prevents fabricated clinical/demographic
information.

## 4. Sensitive Identifier Finding

The raw Patient resource included an SSN-like identifier using the FHIR
US SSN identifier system.

### Engineering decision

The identifier was retained only in the raw source representation and
was not extracted into Silver or Gold.

Reason:

-   It was not required for care-gap analytics.
-   Propagating it would increase unnecessary exposure.
-   The project demonstrates data minimization.

## 5. Observation Data Findings

The Observation dataset contained a large number of clinical
measurements.

Current Silver Observation validation:

-   613,600 observations
-   613,600 unique observation IDs
-   0 missing observation IDs
-   0 missing patient IDs
-   9,049 HbA1c observations
-   9,049 numeric HbA1c values
-   0 non-numeric HbA1c values

HbA1c values observed:

-   Minimum: 2.3
-   Maximum: 11.28

The pipeline therefore preserves the source measurement while enabling
numeric analytical use.

## 6. Condition Coding Issue

One of the most important analytical findings was that "diabetes" could
not safely be defined by simply searching every condition containing the
word diabetes.

The dataset contained both:

-   Primary Type 2 diabetes
-   Diabetes-related complications

Examples included kidney disease, microalbuminuria, proteinuria,
neuropathy, retinopathy, and blindness related to diabetes.

A broad diabetes-condition union produced an inflated population because
complication conditions overlapped with the same patients.

### Correction

The Gold diabetes cohort was rebuilt using the exact primary Type 2
diabetes code:

``` text
44054006
```

This produced:

``` text
96 Type 2 diabetes patients
```

### Engineering lesson

Business definitions should be based on explicit clinical coding
requirements rather than broad text matching whenever a controlled
terminology is available.

## 7. Hypertension Definition

The hypertension population was identified from the hypertension
condition coding used by the synthetic dataset.

Current result:

``` text
274 hypertension patients
```

The Gold model then evaluates blood-pressure observation recency for
this cohort.

## 8. Encounter Data Problem

The Encounter resource initially exposed a significant data-quality
issue.

Current validation:

``` text
Total encounters:       71,751
Unique encounters:      71,751
Missing encounter ID:        0
Missing patient ID:       6,396
```

The missing patient IDs were investigated against the raw Bronze FHIR
records.

The records genuinely lacked a usable `subject.reference` to a Patient
resource.

## 9. Encounter Quarantine

Instead of dropping those records, the pipeline writes them to:

``` text
workspace.default.quarantine_encounter
```

Result:

``` text
6,396 quarantined encounters
6,396 unique quarantined encounters
```

Approximate quarantine rate:

``` text
8.9%
```

This creates an explicit failure path:

``` text
Encounter
   |
   v
Validate patient reference
   |
   +---- valid ----> Silver / Gold
   |
   +---- invalid --> quarantine
```

## 10. Patient 360 Join Handling

Patient 360 combines:

-   Patient information
-   Diabetes care gaps
-   Hypertension care gaps
-   Encounter information

Only encounters with a valid patient ID are included in patient-level
encounter aggregation.

Current Patient 360 validation:

-   1,141 total patients
-   1,141 unique patients
-   96 diabetes patients
-   274 hypertension patients
-   1,076 patients with valid linked encounters

The 65 patients without a valid linked encounter are not fabricated or
force-matched.

## 11. Diabetes Care-Gap Results

The Gold diabetes model identifies the latest HbA1c for each Type 2
diabetes patient.

Current results:

``` text
Type 2 diabetes patients: 96
HbA1c care gaps:          25
Up to date:               71
Care-gap rate:            26.04%
```

The care-gap rule used in the project is:

``` text
No HbA1c
OR
More than 365 days since latest HbA1c
→ care_gap
```

Otherwise:

``` text
up_to_date
```

## 12. Hypertension Care-Gap Results

Current results:

``` text
Hypertension patients:    274
BP care gaps:              67
Up to date:               207
Care-gap rate:             24.45%
```

The same recency principle is applied to the latest blood-pressure
observation.

## 13. dbt Modeling Issue

The first analytics models were intentionally built after Gold was
validated.

The dbt layer separates:

``` text
Staging
   ↓
Intermediate
   ↓
Marts
```

The intermediate model derives:

``` text
care_gap_type
```

including:

-   `diabetes_and_hypertension`
-   `diabetes`
-   `hypertension`
-   `none`

The final patient mart supports the dashboard's operational table.

## 14. dbt Validation

The final full dbt build completed successfully:

``` text
6 models
12 data tests
18 total resources

PASS=18
WARN=0
ERROR=0
SKIP=0
```

Tests cover:

-   Not-null patient IDs
-   Unique patient IDs
-   Accepted care-gap values
-   Accepted condition-status values
-   Required mart metrics

## 15. Terraform Finding

Terraform was introduced after the data and analytics layers were
working.

The purpose is infrastructure management, not data transformation.

Terraform successfully:

-   Initialized the Databricks provider
-   Authenticated using the configured Databricks profile
-   Read the workspace catalog
-   Created `workspace.healthcare_analytics`
-   Reached an idempotent plan with no changes

Validation:

``` text
terraform fmt -check -recursive
terraform validate
terraform plan
```

## 16. Snowflake Integration Limitation

Snowflake was provisioned as an enterprise analytics target.

A Databricks Open Sharing / Delta Sharing integration was investigated.

The Snowflake Trial environment returned:

``` text
DS_GATEKEEPER_DISABLED
```

for the required feature.

### Engineering decision

The integration was not represented as fully successful.

Instead, the project documents:

-   What was configured
-   What was verified
-   The platform limitation
-   The resulting architecture decision

This is preferable to claiming an integration that could not be
validated.

## 17. Omni Limitation

Omni was considered as the BI layer but could not be implemented through
the available signup path because the required work-email access was
unavailable.

### Decision

Databricks SQL Dashboard was selected as the implemented BI layer.

The dashboard now provides:

-   Executive KPIs
-   Condition-level care-gap rates
-   Encounter data quality
-   Patient-level care gaps

## 18. Dashboard Results

Current dashboard KPIs:

``` text
Total patients:                 1,141
Diabetes care gaps:                25
Hypertension care gaps:            67
Patients with any care gap:        73
```

Condition-level rates:

``` text
Diabetes:       26.04%
Hypertension:   24.45%
```

Encounter quality:

``` text
Total:          71,751
Valid:          65,355
Quarantined:     6,396
```

## 19. Engineering Lessons

The main lessons from the implementation were:

1.  FHIR data is nested and requires deliberate normalization.
2.  Raw data should be preserved before transformation.
3.  Healthcare cohort definitions should use explicit clinical codes.
4.  Text matching can produce inflated populations.
5.  Missing references should be measured and investigated.
6.  Invalid records should be quarantined instead of silently discarded.
7.  Null source values should not be replaced with invented values.
8.  Sensitive identifiers should not be propagated when unnecessary.
9.  Business logic belongs in an explicit analytics layer.
10. Infrastructure should be reproducible through Infrastructure as
    Code.
11. External platform limitations should be documented honestly.
12. Dashboards should expose both business outcomes and data-quality
    context.

## 20. Current Platform Status

The core implementation is complete:

``` text
FHIR ingestion                 COMPLETE
Bronze                         COMPLETE
Silver                         COMPLETE
Data quality/quarantine        COMPLETE
Gold                           COMPLETE
dbt models                     COMPLETE
dbt tests                      18/18 PASS
Terraform                       COMPLETE
CI validation                  COMPLETE
Databricks SQL dashboard       COMPLETE
Snowflake sharing              BLOCKED BY TRIAL FEATURE
Omni integration               NOT IMPLEMENTED
```
