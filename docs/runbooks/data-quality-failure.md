# Runbook: Data Quality Failure

## Purpose

Provide a repeatable process when healthcare data-quality checks fail.

## Failure Workflow

```text
Data Quality Failure
        |
        v
Identify failed rule
        |
        v
Measure affected records
        |
        v
Inspect source FHIR
        |
        v
Determine root cause
        |
        +-- source issue --> quarantine / document
        |
        +-- transformation issue --> fix code
        |
        +-- business-definition issue --> update logic / ADR
        |
        v
Re-run validation
        |
        v
Rebuild downstream models
```

## Known Example: Missing Encounter Patient Reference

The project found 6,396 encounters without a valid `subject.reference`.

The investigation showed the source records genuinely lacked a usable patient reference.

Decision:

- Do not force a patient match.
- Quarantine the records.
- Exclude them from patient-level encounter aggregation.
- Preserve them for investigation.

## Known Example: Diabetes Cohort Inflation

A broad condition-text definition incorrectly included diabetes-related complications.

This inflated the apparent diabetes population.

Resolution:

- Inspect condition codes.
- Identify the primary Type 2 diabetes code.
- Use `44054006` for the primary Type 2 diabetes cohort.
- Rebuild the Gold model.
- Revalidate the dashboard.

## Known Example: Missing Demographics

The Patient dataset contained missing birth dates and gender values.

Resolution:

- Preserve nulls.
- Do not invent demographic values.
- Allow downstream analytics to handle missingness explicitly.

## Validation After Remediation

Run:

```powershell
dbt build
```

Expected final result for the current project:

```text
PASS=18
WARN=0
ERROR=0
SKIP=0
```

Then refresh the Databricks SQL Dashboard.
