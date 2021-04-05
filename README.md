[![Board Status](https://brianjacdev.visualstudio.com/27939cff-d9e6-4e8a-a169-e9838ab2e691/614ebdd1-1b38-478a-801c-9b3bbcb33ff3/_apis/work/boardbadge/6556c3b7-9a71-40fa-bfa9-ace4714c590e)](https://brianjacdev.visualstudio.com/27939cff-d9e6-4e8a-a169-e9838ab2e691/_boards/board/t/614ebdd1-1b38-478a-801c-9b3bbcb33ff3/Microsoft.RequirementCategory)
# Deploy Function App using the Schedule Trigger for getting Oracle Cloud Audit Events data into Azure Sentinel
This function app will poll Oracle Cloud Audit Events API every 5 mins for logs.  It is designed to get AuditEvents.

## Configuration and Deployment
### Azure Configuration
1. Create an Azure Function on Linux for Python using the Timer trigger
2. Create a Managed Service Identity (MSI) for the function
3. Go to Azure Sentinel Workspace and IAM Blade and add OCI Data Function as a Reader Role
4. Deploy the function application code to the Azure Function, note the Azure Storage Account associated with this Function App

### Oracle Configuration
1. Add Oracle Confidential App, Generate Base 64 ClientID:ClientSecret string, and Find IDCS Uri
2. Review: https://docs.oracle.com/en/cloud/paas/identity-cloud/17.3.6/rest-api/OATOAuthClientWebApp.html


### Application Settings
    "USER_OCID": "ocid1.user....",
    "LOG_ANALYTICS_CUSTID": "XXXXX-XXX-XXXX-XXXX-XXXXXXXXXX",
    "LOG_ANALYTICS_KEY": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX==",
    "LOG_ANALYTICS_LOGTYPE": "OCIAudit",
    "AZURE_TENANT_ID" : "XXXXXXX-XXXXX-XXXXX-XXXXXXX-XXXXXXXXXXXX",
    "AZURE_CLIENT_ID" : "XXXXXXX-XXXX-XXXXXX-XXX-XXXXXXXXXX",
    "AZURE_CLIENT_SECRET" : "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    "OCI_KEY_CONTENT": "-----BEGIN RSA PRIVATE KEY-----\nProc-Type: 4,...",
    "OCI_PASS_PHRASE": "********",
    "OCI_TENANCY" : "ocid1.tenancy.oc1....",
    "OCI_REGION" : "us-ashburn-1"


### Terraform
The Terraform will deploy Azure Key Vault store the Oracle Cloud Infrastructure details that are needed.   The OCI_KEY_CONTENT secret is the content of the key file.   There are a number of ways to import this into a Key Vault secret  The Azure Function uses Key Vault references in its App Settings so these secrets are made available via the os.environ[] dictionary, which simplifies the code and improves portability.
