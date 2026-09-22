from pyspark.sql.window import Window
from pyspark.sql import functions as F


CONDITION_TABLE = "workspace.default.silver_condition"
PATIENT_TABLE = "workspace.default.silver_patient"
OBSERVATION_TABLE = "workspace.default.silver_observation"

GOLD_TABLE = "workspace.default.gold_diabetes_care_gap"


# Type 2 diabetes SNOMED CT code.
TYPE_2_DIABETES_CODE = "44054006"


# ---------------------------------------------------------
# 1. Identify the Type 2 diabetes population
# ---------------------------------------------------------

diabetes_patients = (
    spark.table(CONDITION_TABLE)
    .filter(
        F.col("condition_code") == TYPE_2_DIABETES_CODE
    )
    .select("patient_id")
    .distinct()
)


# ---------------------------------------------------------
# 2. Identify HbA1c observations
# ---------------------------------------------------------

hba1c = (
    spark.table(OBSERVATION_TABLE)
    .filter(
        F.lower(F.col("display")).like("%hba1c%")
        | F.lower(F.col("display")).like("%hemoglobin a1c%")
    )
    .select(
        "patient_id",
        F.to_timestamp("effective_datetime").alias(
            "effective_ts"
        ),
        F.try_cast(
            F.col("value"),
            "double"
        ).alias("hba1c_value"),
        "unit",
    )
    .filter(F.col("patient_id").isNotNull())
)


# ---------------------------------------------------------
# 3. Select the latest HbA1c for each patient
# ---------------------------------------------------------

latest_hba1c = (
    hba1c
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
# 4. Build the diabetes care-gap mart
# ---------------------------------------------------------

gold_diabetes = (
    diabetes_patients.alias("d")
    .join(
        spark.table(PATIENT_TABLE).alias("p"),
        F.col("d.patient_id") == F.col("p.patient_id"),
        "inner",
    )
    .join(
        latest_hba1c.alias("h"),
        F.col("d.patient_id") == F.col("h.patient_id"),
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
        F.col("h.effective_ts").alias(
            "latest_hba1c_date"
        ),
        F.col("h.hba1c_value").alias(
            "latest_hba1c_value"
        ),
        F.col("h.unit").alias(
            "latest_hba1c_unit"
        ),
        F.datediff(
            F.current_date(),
            F.to_date("h.effective_ts"),
        ).alias("days_since_hba1c"),
        F.when(
            F.col("h.effective_ts").isNull(),
            "care_gap",
        )
        .when(
            F.datediff(
                F.current_date(),
                F.to_date("h.effective_ts"),
            ) > 365,
            "care_gap",
        )
        .otherwise("up_to_date")
        .alias("hba1c_care_gap"),
        F.current_date().alias("analysis_date"),
    )
)


(
    gold_diabetes
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(GOLD_TABLE)
)