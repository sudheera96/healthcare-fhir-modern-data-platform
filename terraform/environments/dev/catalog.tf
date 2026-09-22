data "databricks_catalog" "workspace" {
  name = "workspace"
}

output "workspace_catalog" {
  value = data.databricks_catalog.workspace.name
}
