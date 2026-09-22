terraform {
  required_version = ">= 1.6.0"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.100"
    }
  }
}

provider "databricks" {
  profile = "dbc-15721da9-918a"
}
