resource "azurerm_resource_group" "ocifun" {
  name     = var.resourceGroup
  location = var.location
}

resource "azurerm_storage_account" "ocifun" {
  name                     = "${var.ociFunctionName}stor"
  resource_group_name      = azurerm_resource_group.ocifun.name
  location                 = azurerm_resource_group.ocifun.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "ocifun" {
  name                = "${var.ociFunctionName}-service-plan"
  location            = azurerm_resource_group.ocifun.location
  resource_group_name = azurerm_resource_group.ocifun.name
  kind                = "FunctionApp"
  reserved            = true

  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

resource "azurerm_application_insights" "logging" {
  name                = "${var.ociFunctionName}-ai"
  location            = azurerm_resource_group.ocifun.location
  resource_group_name = azurerm_resource_group.ocifun.name
  application_type    = "web"
}

resource "azurerm_key_vault" "ocifun" {
  name                        = var.KeyVaultName
  location                    = azurerm_resource_group.ocifun.location
  resource_group_name         = azurerm_resource_group.ocifun.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_enabled         = true
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "get", "create", "list", "delete"
    ]

    secret_permissions = [
      "get", "set", "list", "delete"
    ]

    storage_permissions = [
      "get", "set", "list", "delete"
    ]
  }
}

resource "azurerm_key_vault_secret" "ocikey" {
  name         = "oci-key"
  value        = var.ocikey
  key_vault_id = azurerm_key_vault.ocifun.id
}

resource "azurerm_key_vault_secret" "ocifingerprint" {
  name         = "oci-fingerprint"
  value        = var.ocifingerprint
  key_vault_id = azurerm_key_vault.ocifun.id
}

resource "azurerm_key_vault_secret" "ocipassphrase" {
  name         = "oci-passphrase"
  value        = var.ocipassphrase
  key_vault_id = azurerm_key_vault.ocifun.id
}

resource "azurerm_key_vault_secret" "loganalyticskey" {
  name         = "loganalytics-key"
  value        = var.loganalyticskey
  key_vault_id = azurerm_key_vault.ocifun.id
}

resource "azurerm_key_vault_secret" "clientsecret" {
  name         = "clientsecret"
  value        = var.clientsecret
  key_vault_id = azurerm_key_vault.ocifun.id
}

resource "azurerm_function_app" "ocifun" {
  name                          = var.ociFunctionName
  location                      = azurerm_resource_group.ocifun.location
  resource_group_name           = azurerm_resource_group.ocifun.name
  app_service_plan_id           = azurerm_app_service_plan.ocifun.id
  storage_account_name          = azurerm_storage_account.ocifun.name
  storage_account_access_key    = azurerm_storage_account.ocifun.primary_access_key
  os_type                       = "linux"

  identity { 
      type = "SystemAssigned" 
  }

  app_settings = {
    "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.logging.instrumentation_key
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "FUNCTIONS_EXTENSION_VERSION" = "~3"
    "AzureWebJobsStorage" = "UseDevelopmentStorage=true"
    "LOG_ANALYTICS_CUSTID" = var.loganalyticsworkspace
    "LOG_ANALYTICS_LOGTYPE" = "OCIAudit"
    "AZURE_TENANT_ID"  = var.tenantid
    "AZURE_CLIENT_ID"  = var.clientid
    "USER_OCID" = var.ociuser
    "OCI_TENANCY"  = var.ocitenancy
    "OCI_REGION"  = var.ociregion
    "LOG_ANALYTICS_KEY" = "@Microsoft.KeyVault(SecretUri=https://${azurerm_key_vault_secret.loganalyticskey.id})"
    "AZURE_CLIENT_SECRET" = "@Microsoft.KeyVault(SecretUri=https://${azurerm_key_vault_secret.clientsecret.id})"
    "OCI_KEY_CONTENT" = "@Microsoft.KeyVault(SecretUri=https://${azurerm_key_vault_secret.ocikey.id})"
    "OCI_FINGERPRINT" = "@Microsoft.KeyVault(SecretUri=https://${azurerm_key_vault_secret.ocifingerprint.id})"
    "OCI_PASS_PHRASE" = "@Microsoft.KeyVault(SecretUri=https://${azurerm_key_vault_secret.ocipassphrase.id})"
  }

  # The FUNCTIONS_EXTENSION_VERSION must be ~3 or higher, prevent overwrite to ~1
  lifecycle { 
      ignore_changes = [ app_settings["FUNCTIONS_EXTENSION_VERSION"] ] 
  }

}

resource "azurerm_key_vault_access_policy" "ocifun" {
  key_vault_id = azurerm_key_vault.ocifun.id  
  tenant_id = azurerm_function_app.ocifun.identity[0].tenant_id
  object_id = azurerm_function_app.ocifun.identity[0].principal_id

  key_permissions = [
    "get",
  ]

  secret_permissions = [
    "get",
  ]

  storage_permissions = [
    "get",
  ]
}
