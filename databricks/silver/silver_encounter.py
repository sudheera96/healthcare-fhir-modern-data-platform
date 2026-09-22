from pyspark.sql import functions as F


BRONZE_TABLE = "workspace.default.bronze_fhir_encounter"
SILVER_TABLE = "workspace.default.silver_encounter"


bronze_encounter = spark.table(BRONZE_TABLE)

silver_encounter = (
    bronze_encounter
    .select(
        F.col("resource_id").alias("encounter_id"),

        F.get_json_object(
            "raw_json",
            "$.subject.reference"
        ).alias("patient_reference"),

        F.regexp_extract(
            F.get_json_object(
                "raw_json",
                "$.subject.reference"
            ),
            r"Patient/(.*)",
            1
        ).alias("patient_id"),

        F.get_json_object(
            "raw_json",
            "$.status"
        ).alias("status"),

        F.get_json_object(
            "raw_json",
            "$.class.code"
        ).alias("encounter_class"),

        F.get_json_object(
            "raw_json",
            "$.class.display"
        ).alias("encounter_class_display"),

        F.get_json_object(
            "raw_json",
            "$.period.start"
        ).alias("start_datetime"),

        F.get_json_object(
            "raw_json",
            "$.period.end"
        ).alias("end_datetime"),

        F.get_json_object(
            "raw_json",
            "$.serviceProvider.reference"
        ).alias("service_provider_reference"),

        F.get_json_object(
            "raw_json",
            "$.serviceProvider.display"
        ).alias("service_provider_display"),

        F.col("ingestion_timestamp")
    )
)

(
    silver_encounter
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER_TABLE)
)