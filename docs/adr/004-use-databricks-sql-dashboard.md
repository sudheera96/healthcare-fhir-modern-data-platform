# ADR 002: Use dbt for Analytics Modeling

## Status

Accepted

## Context

The Databricks Gold layer produces trusted healthcare datasets, but business-facing analytics logic needs a separate, testable analytics-engineering layer.

## Decision

Use dbt for staging, intermediate, and mart transformations.

## Why

dbt provides:

- SQL-based transformations
- Dependency management through `ref`
- Data tests
- Reproducible builds
- Clear separation between engineering and analytics logic

## Result

The project implements:

- 3 staging models
- 1 intermediate model
- 2 mart models
- 12 data tests

The final full build passed 18/18 resources.

## Consequence

Business logic becomes easier to test and maintain without moving all transformation logic into Python notebooks.
