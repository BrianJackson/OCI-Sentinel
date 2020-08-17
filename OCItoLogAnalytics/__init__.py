import datetime
import logging

import azure.functions as func
from azure.common.credentials import ServicePrincipalCredentials
from azure.loganalytics import LogAnalyticsDataClient
from azure.loganalytics.models import QueryBody

import json
import requests
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import base64
import oci
import os

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    initOCI()

class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(DatetimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)

def initOCI():

    # Set up OCI config
    config = oci.config.from_file(
        os.environ["OCI_PATH_TO_CONFIG"],
        "DEFAULT")

    # Create a service client
    identity = oci.identity.IdentityClient(config)

    tenancy_id = config["tenancy"]
    # Update the customer ID to your Log Analytics workspace ID
    customer_id = os.environ["LOG_ANALYTICS_CUSTID"]

    # For the shared key, use either the primary or the secondary Connected Sources client authentication key   
    shared_key = os.environ["LOG_ANALYTICS_KEY"]
    log_type = os.environ["LOG_ANALYTICS_LOGTYPE"]

    #  Initiate the client with the locally available config.
    identity = oci.identity.IdentityClient(config)

    #  Timespan defined by variables start_time and end_time(today).
    #  ListEvents expects timestamps into RFC3339 format.
    #  For the purposes of sample script, logs of last 5 days.
    end_time = datetime.utcnow()

    # Query Log Analytics for lastest date/time in OCIAudit table and pass.
    start_time = get_start_time(log_type)
    print('Start time is: {0}'.format(start_time))
 
    # This array will be used to store the list of available regions.
    regions = get_subscription_regions(identity, tenancy_id)

    # This array will be used to store the list of compartments in the tenancy.
    compartments = get_compartments(identity, tenancy_id)

    # Initialize the audit client 
    audit = oci.audit.audit_client.AuditClient(config)

    #  For each region get the logs for each compartment.
    for r in regions:
        #  Initialize with the current region value.
        audit.base_client.set_region(r)

        #  Get audit events for the current region which is specified in the audit object.
        audit_events = get_audit_events(customer_id,
            shared_key,
            audit,
            compartments,
            start_time,
            end_time)

        #  For each audit entry retrieved, post to Log Analytics
        for event in audit_events: 
            jsondoc = json.loads(str(event))
            parsed_json = json.dumps(jsondoc, indent=4, sort_keys=True)
            post_data(customer_id, shared_key, parsed_json, log_type)
            #print(parsed_json)


# Copyright (c) 2016, 2020, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

#  This script retrieves all audit logs across an Oracle Cloud Infrastructure Tenancy.
#  for a timespan defined by start_time and end_time.
#  This sample script retrieves Audit events for last 5 days.
#  This script will work at a tenancy level only.

def get_subscription_regions(identity, tenancy_id):

    # To retrieve the list of all available regions.
    list_of_regions = []
    list_regions_response = identity.list_region_subscriptions(tenancy_id)
    for r in list_regions_response.data:
        list_of_regions.append(r.region_name)
    return list_of_regions


def get_compartments(identity, tenancy_id):

    # Retrieve the list of compartments under the tenancy.
    list_compartments_response = oci.pagination.list_call_get_all_results(
        identity.list_compartments,
        compartment_id=tenancy_id).data

    compartment_ocids = [c.id for c in filter(lambda c: c.lifecycle_state == 'ACTIVE', list_compartments_response)]
 
    return compartment_ocids


def get_audit_events(customer_id, shared_key, audit, compartment_ocids, start_time, end_time):
    '''
    # Get events iteratively for each compartment defined in 'compartments_ocids'
    # for the region defined in 'audit'.
    # This method eagerly loads all audit records in the time range and it does
    # have performance implications of lot of audit records.
    # Ideally, the generator method in oci.pagination should be used to lazily
    # load results.
    '''
    list_of_audit_events = []

    for c in compartment_ocids:
        list_events_response = oci.pagination.list_call_get_all_results(
            audit.list_events,
            compartment_id=c,
            start_time=start_time,
            end_time=end_time).data
        #  Results for a compartment 'c' for a region defined
        #  in 'audit' object.
        list_of_audit_events.extend(list_events_response)
        
    return list_of_audit_events

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8") 
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = f"SharedKey {customer_id}:{encoded_hash}"
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'
    print('URI : ' + uri)
    print('Log Type :' + log_type)
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri, data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
    else:
        print(response.status_code)



def get_start_time(log_type):

    TENANT_ID = os.environ["AZURE_TENANT_ID"]  # AAD Tenant
    CLIENT_ID = os.environ["AZURE_CLIENT_ID"]  # AAD Application / Client ID for registered Service Principal
    KEY = os.environ["AZURE_CLIENT_SECRET"] # # AAD Client Secret
    WORKSPACE_ID = os.environ["LOG_ANALYTICS_CUSTID"] # from the log analytics workspace
    LOG_ANALYTICS_LOGTYPE = os.environ["LOG_ANALYTICS_LOGTYPE"] # The custom log in Log Analytics has '_CL' appended to this name

    credentials = ServicePrincipalCredentials(
        client_id = CLIENT_ID,
        secret = KEY,
        tenant = TENANT_ID,
        resource = "https://api.loganalytics.io "
    )

    client = LogAnalyticsDataClient(credentials, base_url=None)

    workspace_id = WORKSPACE_ID
    body = QueryBody(query = "union isfuzzy=true ({0}_CL |  summarize arg_max(TimeGenerated , TimeGenerated ) |project TimeGenerated ) | summarize arg_max(TimeGenerated , TimeGenerated ) | project TimeGenerated".format(LOG_ANALYTICS_LOGTYPE)) # the query

    query_results = client.query(workspace_id, body) # type: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/loganalytics/azure-loganalytics/azure/loganalytics/models/query_results.py
    table = query_results.tables[0] # https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/loganalytics/azure-loganalytics/azure/loganalytics/models/table.py

    rows = table.rows # [][] of arbitrary data

    start_row = rows[0]
    start_time = start_row[0]

    #Fail safe logic to go back 30 days from now if the start time cannot be parsed to a valid date time
    try:
        start_datetime = datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        start_datetime = datetime.utcnow() + timedelta(days=-30)

    return start_datetime
    

