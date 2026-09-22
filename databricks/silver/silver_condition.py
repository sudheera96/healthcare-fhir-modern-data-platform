from pyspark.sql import functions as F


BRONZE_TABLE = "workspace.default.bronze_fhir_condition"
SILVER_TABLE = "workspace.default.silver_condition"


bronze_condition = spark.table(BRONZE_TABLE)

silver_condition = (
    bronze_condition
    .select(
        F.col("resource_id").alias("condition_id"),

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
            "$.clinicalStatus.coding[0].code"
        ).alias("clinical_status"),

        F.get_json_object(
            "raw_json",
            "$.code.coding[0].system"
        ).alias("code_system"),

        F.get_json_object(
            "raw_json",
            "$.code.coding[0].code"
        ).alias("condition_code"),

        F.get_json_object(
            "raw_json",
            "$.code.coding[0].display"
        ).alias("condition_display"),

        F.when(
            F.lower(
                F.get_json_object(
                    "raw_json",
                    "$.code.coding[0].display"
                )
            ).like("%diabet%"),
            "diabetes"
        )
        .when(
            F.lower(
                F.get_json_object(
                    "raw_json",
                    "$.code.coding[0].display"
                )
            ).like("%hyperten%"),
            "hypertension"
        )
        .when(
            F.lower(
                F.get_json_object(
                    "raw_json",
                    "$.code.coding[0].display"
                )
            ).like("%prediabet%"),
            "prediabetes"
        )
        .otherwise("other")
        .alias("condition_group"),

        F.get_json_object(
            "raw_json",
            "$.onsetDateTime"
        ).alias("onset_datetime"),

        F.get_json_object(
            "raw_json",
            "$.recordedDate"
        ).alias("recorded_date"),

        F.col("ingestion_timestamp")
    )
)

(
    silver_condition
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER_TABLE)
)