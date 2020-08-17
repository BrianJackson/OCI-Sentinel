# TimerTrigger - Python

The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function every 5 minutes.

## How it works

For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 5 minutes is `0 */5 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 5, for any hour, day of the month, month, day of the week, or year".

## Learn more

<TODO> Documentation

    "USER_OCID": "ocid1.user.XXX..XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "OCI_PATH_TO_CONFIG": "./.oci/config",
    "LOG_ANALYTICS_CUSTID": "XXXXX-XXX-XXXX-XXXX-XXXXXXXXXX",
    "LOG_ANALYTICS_KEY": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX==",
    "LOG_ANALYTICS_LOGTYPE": "OCIAudit",
    "AZURE_TENANT_ID" : "XXXXXXX-XXXXX-XXXXX-XXXXXXX-XXXXXXXXXXXX",
    "AZURE_CLIENT_ID" : "XXXXXXX-XXXX-XXXXXX-XXX-XXXXXXXXXX",
    "AZURE_CLIENT_SECRET" : "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

