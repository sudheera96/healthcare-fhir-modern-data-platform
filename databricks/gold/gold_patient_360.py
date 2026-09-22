from pyspark.sql import functions as F


PATIENT_TABLE = "workspace.default.silver_patient"
DIABETES_TABLE = "workspace.default.gold_diabetes_care_gap"
HYPERTENSION_TABLE = "workspace.default.gold_hypertension_care_gap"
ENCOUNTER_TABLE = "workspace.default.silver_encounter"

GOLD_TABLE = "workspace.default.gold_patient_360"


# ---------------------------------------------------------
# 1. Patient base
# ---------------------------------------------------------

patients = spark.table(PATIENT_TABLE)


# ---------------------------------------------------------
# 2. Diabetes care-gap information
# ---------------------------------------------------------

diabetes = (
    spark.table(DIABETES_TABLE)
    .select(
        "patient_id",
        F.lit("Yes").alias("diabetes_status"),
        "latest_hba1c_date",
        "latest_hba1c_value",
        "latest_hba1c_unit",
        "days_since_hba1c",
        "hba1c_care_gap",
    )
)


# ---------------------------------------------------------
# 3. Hypertension care-gap information
# ---------------------------------------------------------

hypertension = (
    spark.table(HYPERTENSION_TABLE)
    .select(
        "patient_id",
        F.lit("Yes").alias("hypertension_status"),
        "latest_bp_date",
        "systolic_bp",
        "diastolic_bp",
        "days_since_bp",
        "bp_care_gap",
    )
)


# ---------------------------------------------------------
# 4. Encounter summary
# ---------------------------------------------------------

encounters = (
    spark.table(ENCOUNTER_TABLE)
    .filter(
        F.col("patient_id").isNotNull()
        & (F.col("patient_id") != "")
    )
    .groupBy("patient_id")
    .agg(
        F.count("*").alias("total_encounters"),
        F.max(
            F.to_timestamp("start_datetime")
        ).alias("last_encounter_date"),
    )
)


# ---------------------------------------------------------
# 5. Build Patient 360
# ---------------------------------------------------------

gold_patient_360 = (
    patients.alias("p")

    .join(
        diabetes.alias("d"),
        F.col("p.patient_id") == F.col("d.patient_id"),
        "left",
    )

    .join(
        hypertension.alias("h"),
        F.col("p.patient_id") == F.col("h.patient_id"),
        "left",
    )

    .join(
        encounters.alias("e"),
        F.col("p.patient_id") == F.col("e.patient_id"),
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

        F.coalesce(
            F.col("d.diabetes_status"),
            F.lit("No"),
        ).alias("diabetes_status"),

        F.coalesce(
            F.col("h.hypertension_status"),
            F.lit("No"),
        ).alias("hypertension_status"),

        F.col("d.latest_hba1c_date"),
        F.col("d.latest_hba1c_value"),
        F.col("d.latest_hba1c_unit"),
        F.col("d.days_since_hba1c"),
        F.col("d.hba1c_care_gap"),

        F.col("h.latest_bp_date"),
        F.col("h.systolic_bp"),
        F.col("h.diastolic_bp"),
        F.col("h.days_since_bp"),
        F.col("h.bp_care_gap"),

        F.coalesce(
            F.col("e.total_encounters"),
            F.lit(0),
        ).alias("total_encounters"),

        F.col("e.last_encounter_date"),

        F.current_date().alias("analysis_date"),
    )
)


# ---------------------------------------------------------
# 6. Persist Patient 360
# ---------------------------------------------------------

(
    gold_patient_360
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(GOLD_TABLE)
)