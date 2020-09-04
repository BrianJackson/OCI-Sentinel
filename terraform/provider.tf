#Set the terraform required version
terraform {
  required_version = "~> 0.12"
}

# Configure the Azure Provider
provider "azurerm" {
  # It is recommended to pin to a given version of the Provider
  version = "2.25"
  features {
    key_vault {
        purge_soft_delete_on_destroy = true
    }
  }
}

# Make client_id, tenant_id, subscription_id and object_id variables
data "azurerm_client_config" "current" {}