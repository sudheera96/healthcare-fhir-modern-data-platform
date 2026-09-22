from pyspark.sql import functions as F


RAW_BASE = "/Volumes/workspace/default/fhir_raw"


def ingest_fhir_resource(resource_name: str) -> str:
    """
    Ingest a FHIR NDJSON resource into a Bronze Delta table.

    Bronze preserves the original FHIR resource as raw_json while
    adding ingestion metadata for traceability.
    """

    raw_path = f"{RAW_BASE}/{resource_name}.ndjson"
    bronze_table = f"workspace.default.bronze_fhir_{resource_name.lower()}"

    df = (
        spark.read
        .text(raw_path)
        .withColumnRenamed("value", "raw_json")
        .withColumn(
            "source_file",
            F.col("_metadata.file_path")
        )
        .withColumn(
            "ingestion_timestamp",
            F.current_timestamp()
        )
        .withColumn(
            "resource_type",
            F.get_json_object(
                "raw_json",
                "$.resourceType"
            )
        )
        .withColumn(
            "resource_id",
            F.get_json_object(
                "raw_json",
                "$.id"
            )
        )
    )

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(bronze_table)
    )

    return bronze_table


CORE_RESOURCES = [
    "Patient",
    "Encounter",
    "Condition",
    "Observation",
    "DiagnosticReport",
    "MedicationRequest",
    "MedicationAdministration",
    "Procedure",
    "CarePlan",
    "CareTeam",
    "AllergyIntolerance",
    "Immunization",
    "Device",
]


for resource in CORE_RESOURCES:
    table_name = ingest_fhir_resource(resource)
    print(f"Ingested {resource} -> {table_name}")