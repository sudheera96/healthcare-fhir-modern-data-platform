# Data Quality

This directory contains data-quality validation and quarantine logic for
the healthcare FHIR analytics platform.

## Encounter Quality Rule

Every encounter used for patient-level analytics must contain a valid
FHIR patient reference.

Records where `patient_id` is null or empty are quarantined rather than
silently dropped.

### Current validation result

- Total encounters: 71,751
- Valid encounters: 65,355
- Quarantined encounters: 6,396
- Quarantine rate: approximately 8.9%

### Failure-handling pattern

```text
Silver Encounter
       |
       v
Validate patient reference
       |
   +---+---+
   |       |
 PASS     FAIL
   |       |
   v       v
Gold     Quarantine
         + error metrics
         + investigation