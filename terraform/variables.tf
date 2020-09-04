variable "resourceGroup" {
  type        = string
  description = "Resource Group name"
}

variable "location" {
  type        = string
  description = "Azure region where to create resources."
}

variable "ociFunctionName" {
  type        = string
  description = "The name of the Function which sends OCI audit entries to Log Analytics"
}

variable "KeyVaultName" {
  type        = string
  description = "The name of the Key Vault that contains the OCI config, key, and Log Analytics secrets"
}

variable "ocikey" {
  type         = string
  description  = "OCI RSA Key content.  This value is stored as a Key Vault secret"
}

variable "ocifingerprint" {
  type         = string
  description  = "OCI RSA Key thumbprint.  This value is stored as a Key Vault secret"
}

variable "ocipassphrase" {
  type         = string
  description  = "OCI RSA Key passphrase.  This value is stored as a Key Vault secret"
}

variable "loganalyticskey" {
  type         = string
  description  = "Log Analytics workspace key.  This value is stored as a Key Vault secret"
 }

variable "loganalyticsworkspace" {
  type         = string
  description  = "Log Analytics workspace ID"
}

variable "clientid" {
  type         = string
  description  = "Service Principal client ID/app ID for accessing Log Analytics workspace"
}

variable "tenantid" {
  type         = string
  description  = "Service Principal tenant ID for accessing Log Analytics workspace"
}

variable "clientsecret" {
  type         = string
  description  = "Service Principal secret for accessing Log Analytics workspace"
}

variable "ociuser" {
  type         = string
  description  = "OCI user ID"
 }

variable "ocitenancy" {
  type         = string
  description  = "OCI tenancy"
 }

variable "ociregion" {
  type         = string
  description  = "OCI region"
}