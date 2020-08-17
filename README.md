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
3. Navigate to the Azure Storage Account for the Function.  The account name can be found in the Application Settings - AzureWebJobsStorage key
4. Select the file share and navigate to "/site/wwwwroot/" and add your OCI configuration folder here.   In the localsettings.sample.json, there is a relative path to a folder the folder which is called /.oci
4. Copy the configuration folder to a location 
