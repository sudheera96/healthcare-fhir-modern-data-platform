from pyspark.sql import functions as F


SILVER_TABLE = "workspace.default.silver_encounter"
QUARANTINE_TABLE = "workspace.default.quarantine_encounter"


silver_encounter = spark.table(SILVER_TABLE)


# ---------------------------------------------------------
# 1. Identify invalid encounter records
# ---------------------------------------------------------
# An encounter must have a patient reference before it can
# safely participate in patient-level analytics.

quarantine_encounter = (
    silver_encounter
    .filter(
        F.col("patient_id").isNull()
        | (F.col("patient_id") == "")
    )
)


# ---------------------------------------------------------
# 2. Persist quarantined records
# ---------------------------------------------------------

(
    quarantine_encounter
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(QUARANTINE_TABLE)
)


# ---------------------------------------------------------
# 3. Produce quality metrics
# ---------------------------------------------------------

total_encounters = silver_encounter.count()

valid_encounters = (
    silver_encounter
    .filter(
        F.col("patient_id").isNotNull()
        & (F.col("patient_id") != "")
    )
    .count()
)

quarantined_encounters = quarantine_encounter.count()

quarantine_rate = (
    (quarantined_encounters / total_encounters) * 100
    if total_encounters > 0
    else 0
)


quality_metrics = spark.createDataFrame(
    [
        (
            "encounter",
            total_encounters,
            valid_encounters,
            quarantined_encounters,
            round(quarantine_rate, 2),
        )
    ],
    [
        "resource_type",
        "total_records",
        "valid_records",
        "quarantined_records",
        "quarantine_rate_pct",
    ],
)


display(quality_metrics)