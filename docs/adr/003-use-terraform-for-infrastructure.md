# ADR 004: Use Databricks SQL Dashboard for BI

## Status

Accepted

## Context

The project needs a business-facing interface so users can see healthcare care-gap results without querying tables manually.

Omni was considered but could not be implemented through the available signup/access path.

## Decision

Use Databricks SQL Dashboard as the implemented BI layer.

## Dashboard Scope

The dashboard includes:

- Total patients
- Diabetes care gaps
- Hypertension care gaps
- Patients with any care gap
- Care-gap rate by condition
- Encounter data quality
- Patient-level care-gap details

## Alternatives

### Omni

Potential future downstream BI consumer, but not implemented in this project.

### Power BI

Possible future integration, but would introduce another platform that was not necessary to demonstrate the end-to-end workflow.

## Consequence

The dashboard remains close to the Databricks data platform and can directly expose the validated analytics models.
