resource "databricks_schema" "healthcare_analytics" {
  catalog_name = "workspace"
  name         = "healthcare_analytics"

  comment = "Healthcare FHIR analytics platform managed by Terraform"
}

output "healthcare_schema" {
  value = databricks_schema.healthcare_analytics.name
}
