from pyspark.sql import functions as F


BRONZE_TABLE = "workspace.default.bronze_fhir_patient"
SILVER_TABLE = "workspace.default.silver_patient"


bronze_patient = spark.table(BRONZE_TABLE)

silver_patient = (
    bronze_patient
    .select(
        F.col("resource_id").alias("patient_id"),

        F.get_json_object(
            "raw_json",
            "$.name[0].given[0]"
        ).alias("first_name"),

        F.get_json_object(
            "raw_json",
            "$.name[0].family"
        ).alias("last_name"),

        F.get_json_object(
            "raw_json",
            "$.gender"
        ).alias("gender"),

        F.get_json_object(
            "raw_json",
            "$.birthDate"
        ).alias("birth_date"),

        F.get_json_object(
            "raw_json",
            "$.address[0].city"
        ).alias("city"),

        F.get_json_object(
            "raw_json",
            "$.address[0].state"
        ).alias("state"),

        F.get_json_object(
            "raw_json",
            "$.address[0].postalCode"
        ).alias("postal_code"),

        F.get_json_object(
            "raw_json",
            "$.address[0].country"
        ).alias("country"),

        F.col("ingestion_timestamp")
    )
)

(
    silver_patient
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER_TABLE)
)