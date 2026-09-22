from pyspark.sql import functions as F


BRONZE_TABLE = "workspace.default.bronze_fhir_observation"
SILVER_TABLE = "workspace.default.silver_observation"


bronze_observation = spark.table(BRONZE_TABLE)

silver_observation = (
    bronze_observation
    .select(
        F.col("resource_id").alias("observation_id"),

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
            "$.code.coding[0].system"
        ).alias("code_system"),

        F.get_json_object(
            "raw_json",
            "$.code.coding[0].code"
        ).alias("code"),

        F.get_json_object(
            "raw_json",
            "$.code.coding[0].display"
        ).alias("display"),

        F.get_json_object(
            "raw_json",
            "$.effectiveDateTime"
        ).alias("effective_datetime"),

        F.get_json_object(
            "raw_json",
            "$.valueQuantity.value"
        ).alias("value"),

        F.get_json_object(
            "raw_json",
            "$.valueQuantity.unit"
        ).alias("unit"),

        F.get_json_object(
            "raw_json",
            "$.valueQuantity.code"
        ).alias("unit_code"),

        F.get_json_object(
            "raw_json",
            "$.component[0].code.coding[0].display"
        ).alias("component_1_display"),

        F.get_json_object(
            "raw_json",
            "$.component[0].valueQuantity.value"
        ).alias("component_1_value"),

        F.get_json_object(
            "raw_json",
            "$.component[1].code.coding[0].display"
        ).alias("component_2_display"),

        F.get_json_object(
            "raw_json",
            "$.component[1].valueQuantity.value"
        ).alias("component_2_value"),

        F.col("ingestion_timestamp")
    )
)

(
    silver_observation
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER_TABLE)
)