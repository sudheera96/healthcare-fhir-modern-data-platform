# Runbook: FHIR Ingestion

## Purpose

Troubleshoot the FHIR ingestion and Bronze-to-Silver pipeline.

## 1. Check Source Files

Confirm the expected FHIR NDJSON files are available in the Databricks volume.

Check:

- file name
- file size
- resource type
- whether the file contains valid NDJSON records

## 2. Check Bronze

Confirm the Bronze table was created and contains records.

Important fields:

- `raw_json`
- `resource_type`
- `resource_id`
- `source_file`
- `ingestion_timestamp`

## 3. Check Silver

Validate:

- record count
- unique resource IDs
- patient references
- required dates
- expected clinical codes

## 4. Check Quarantine

For Encounter data, inspect:

```text
workspace.default.quarantine_encounter
```

Current known condition:

```text
6,396 encounters lacked a usable patient reference.
```

Do not fabricate patient relationships.

## 5. Check Gold

After Silver validation, verify:

- diabetes cohort count
- hypertension cohort count
- care-gap counts
- Patient 360 population

## 6. Re-run

After correcting source/configuration issues:

1. Re-run Bronze ingestion.
2. Re-run affected Silver transformation.
3. Re-run quality checks.
4. Rebuild Gold tables.
5. Run dbt build.
6. Refresh the Databricks SQL Dashboard.

## 7. Escalation

If record counts change unexpectedly:

- compare with previous run
- inspect source file changes
- inspect quarantined records
- review Git changes
- review Databricks execution logs
