# ADR 003: Use Terraform for Infrastructure

## Status

Accepted

## Context

Databricks infrastructure should be reproducible and reviewable rather than created only through manual UI actions.

## Decision

Use Terraform with the Databricks provider.

## Implemented Scope

Terraform currently manages:

- Databricks provider configuration
- workspace catalog lookup
- `workspace.healthcare_analytics` schema

## Validation

The project successfully ran:

```text
terraform fmt -check -recursive
terraform init
terraform validate
terraform plan
```

The final plan reported no configuration drift.

## Consequences

Benefits:

- Infrastructure as Code
- Git-based review
- Repeatability
- Idempotent changes
- Clear separation between infrastructure and data transformations

Tradeoff:

- Terraform adds configuration and provider-management complexity.
