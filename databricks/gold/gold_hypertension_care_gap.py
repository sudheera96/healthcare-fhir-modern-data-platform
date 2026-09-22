from pyspark.sql import functions as F
from pyspark.sql.window import Window


CONDITION_TABLE = "workspace.default.silver_condition"
PATIENT_TABLE = "workspace.default.silver_patient"
OBSERVATION_TABLE = "workspace.default.silver_observation"

GOLD_TABLE = "workspace.default.gold_hypertension_care_gap"


# Essential hypertension SNOMED CT code.
HYPERTENSION_CODE = "59621000"


# ---------------------------------------------------------
# 1. Identify the hypertension population
# ---------------------------------------------------------

hypertension_patients = (
    spark.table(CONDITION_TABLE)
    .filter(
        F.col("condition_code") == HYPERTENSION_CODE
    )
    .select("patient_id")
    .distinct()
)


# ---------------------------------------------------------
# 2. Identify blood-pressure observations
# ---------------------------------------------------------

blood_pressure = (
    spark.table(OBSERVATION_TABLE)
    .filter(
        F.lower(F.col("display")).like("%blood pressure%")
        | F.lower(F.col("display")).like("%systolic%")
    )
    .select(
        "patient_id",
        F.to_timestamp("effective_datetime").alias(
            "effective_ts"
        ),
        "component_1_display",
        "component_1_value",
        "component_2_display",
        "component_2_value",
    )
    .filter(F.col("patient_id").isNotNull())
)


# ---------------------------------------------------------
# 3. Select the latest blood-pressure observation
# ---------------------------------------------------------

latest_bp = (
    blood_pressure
    .withColumn(
        "row_number",
        F.row_number().over(
            Window.partitionBy("patient_id")
            .orderBy(F.col("effective_ts").desc())
        )
    )
    .filter(F.col("row_number") == 1)
    .drop("row_number")
)


# ---------------------------------------------------------
# 4. Build the hypertension care-gap mart
# ---------------------------------------------------------

gold_hypertension = (
    hypertension_patients.alias("h")
    .join(
        spark.table(PATIENT_TABLE).alias("p"),
        F.col("h.patient_id") == F.col("p.patient_id"),
        "inner",
    )
    .join(
        latest_bp.alias("bp"),
        F.col("h.patient_id") == F.col("bp.patient_id"),
        "left",
    )
    .select(
        F.col("p.patient_id"),
        F.col("p.first_name"),
        F.col("p.last_name"),
        F.col("p.gender"),
        F.col("p.birth_date"),
        F.col("p.city"),
        F.col("p.state"),
        F.col("bp.effective_ts").alias(
            "latest_bp_date"
        ),
        F.col("bp.component_1_value").alias(
            "systolic_bp"
        ),
        F.col("bp.component_2_value").alias(
            "diastolic_bp"
        ),
        F.datediff(
            F.current_date(),
            F.to_date("bp.effective_ts"),
        ).alias("days_since_bp"),
        F.when(
            F.col("bp.effective_ts").isNull(),
            "care_gap",
        )
        .when(
            F.datediff(
                F.current_date(),
                F.to_date("bp.effective_ts"),
            ) > 365,
            "care_gap",
        )
        .otherwise("up_to_date")
        .alias("bp_care_gap"),
        F.current_date().alias("analysis_date"),
    )
)


(
    gold_hypertension
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(GOLD_TABLE)
)