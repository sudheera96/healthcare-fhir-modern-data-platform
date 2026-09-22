from pyspark.sql import functions as F


DIABETES_TABLE = "workspace.default.gold_diabetes_care_gap"
HYPERTENSION_TABLE = "workspace.default.gold_hypertension_care_gap"

GOLD_TABLE = "workspace.default.gold_healthcare_quality_metrics"


# ---------------------------------------------------------
# Diabetes quality metrics
# ---------------------------------------------------------

diabetes_metrics = (
    spark.table(DIABETES_TABLE)
    .select(
        F.lit("Diabetes").alias("condition"),
        F.count("*").alias("total_patients"),
        F.count_if(
            F.col("hba1c_care_gap") == "care_gap"
        ).alias("care_gap_patients"),
        F.count_if(
            F.col("hba1c_care_gap") == "up_to_date"
        ).alias("up_to_date_patients"),
    )
    .withColumn(
        "care_gap_rate",
        F.round(
            F.col("care_gap_patients")
            * 100.0
            / F.col("total_patients"),
            2,
        ),
    )
    .withColumn(
        "analysis_date",
        F.current_date(),
    )
)


# ---------------------------------------------------------
# Hypertension quality metrics
# ---------------------------------------------------------

hypertension_metrics = (
    spark.table(HYPERTENSION_TABLE)
    .select(
        F.lit("Hypertension").alias("condition"),
        F.count("*").alias("total_patients"),
        F.count_if(
            F.col("bp_care_gap") == "care_gap"
        ).alias("care_gap_patients"),
        F.count_if(
            F.col("bp_care_gap") == "up_to_date"
        ).alias("up_to_date_patients"),
    )
    .withColumn(
        "care_gap_rate",
        F.round(
            F.col("care_gap_patients")
            * 100.0
            / F.col("total_patients"),
            2,
        ),
    )
    .withColumn(
        "analysis_date",
        F.current_date(),
    )
)


# ---------------------------------------------------------
# Combine condition-level metrics
# ---------------------------------------------------------

gold_quality_metrics = (
    diabetes_metrics
    .unionByName(hypertension_metrics)
)


# ---------------------------------------------------------
# Persist Gold metrics
# ---------------------------------------------------------

(
    gold_quality_metrics
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(GOLD_TABLE)
)