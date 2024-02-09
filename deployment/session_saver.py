import os
import re
import json
import subprocess
import boto3
import time
import sys
from utility import dynamodb_find_session_events
from utility import dynamodb_delete_session_events


sso_elevator_audit_bucket_name = os.environ.get("SSO_ELEVATOR_AUDIT_BUCKET_NAME", "")
dynamodb_table_name = os.environ.get("DYNAMODB_TABLE_NAME", "")
# sso_elevator_audit_bucket_name = "sso-elevator-audit-7f6d93c4cf4a8a0fa6ffaddfd70817782bddd202"
# dynamodb_table_name = 'sso_elevator_session_events'

def lambda_handler(event, context):
    try:
        # Extract S3 object key from the event data
        s3_object_key = event['detail']['object']['key']

        # Download the log file from S3
        print (f'Downloading the SSO session event log life {s3_object_key} ...')
        s3_client = boto3.client('s3')
        filename = os.path.basename(s3_object_key)
        local_log_file_path = f'/tmp/{filename}'
        file = s3_client.download_file(sso_elevator_audit_bucket_name, s3_object_key, local_log_file_path)

        log_file = open(local_log_file_path, 'r')
        log_file_content = log_file.read()
        log_file_content_json = json.loads(log_file_content)

        session_event_timestamp = log_file_content_json['timestamp']
        session_event_requester_email = log_file_content_json['requester_email']
        session_event_account_id = log_file_content_json['account_id']
        session_operation_type = log_file_content_json['operation_type']

        print(f'Downloaded SSO event log file. The event operation type is: {session_operation_type}.')

        # Put event to the DynamoDB
        if session_operation_type == "grant":
            print('Putting the SSO event to the DynamoDB table...')
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(dynamodb_table_name)
            response = table.put_item(Item=json.loads(log_file_content))
            print("DynamoDB PutItem succeeded")
        
        # Remove event from DynamoDB
        elif session_operation_type == "revoke":
            print('Removing the SSO event from the DynamoDB table...')
            sso_session_events = dynamodb_find_session_events(dynamodb_table_name, 
                                                              session_event_requester_email, 
                                                              session_event_account_id)
            dynamodb_delete_session_events(dynamodb_table_name, 
                                           sso_session_events)

        return {
            'statusCode': 200,
            'body': 'Handler executed successfully'
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        return {
            'statusCode': 500,
            'body': 'Handler encountered an error'
        }

# event={"version":"0","id":"122c2cd7-62ea-b734-476e-5d7f10c44239","detail-type":"Object Created","source":"aws.s3","account":"933561452000","time":"2024-02-08T07:53:43Z","region":"eu-north-1","resources":["arn:aws:s3:::sso-elevator-audit-7f6d93c4cf4a8a0fa6ffaddfd70817782bddd202"],"detail":{"version":"0","bucket":{"name":"sso-elevator-audit-7f6d93c4cf4a8a0fa6ffaddfd70817782bddd202"},"object":{"key":"logs/2024/02/08/c6f61bd5-f538-4ccf-86f2-f51d69b49f7d.json","size":447,"etag":"f5ebb1401ceb384333aef699a164454a","version-id":"5D6Oj1YX_yc2BaDzoQhH8SkAYmRIiJpk","sequencer":"0065C488878DD40529"},"request-id":"476X6HYX8Y30NQ47","requester":"933561452000","source-ip-address":"16.171.111.239","reason":"PutObject"}}
# event={"version":"0","id":"01dfaa72-b7f2-9f22-0111-03d73691600a","detail-type":"Object Created","source":"aws.s3","account":"933561452000","time":"2024-02-08T09:23:58Z","region":"eu-north-1","resources":["arn:aws:s3:::sso-elevator-audit-7f6d93c4cf4a8a0fa6ffaddfd70817782bddd202"],"detail":{"version":"0","bucket":{"name":"sso-elevator-audit-7f6d93c4cf4a8a0fa6ffaddfd70817782bddd202"},"object":{"key":"logs/2024/02/08/07492052-af9b-42ed-a42d-14b733ac0068.json","size":425,"etag":"1851729880c42f2e7809ba9766ce9e28","version-id":"Vs13oJgC_DTHvIE5OkUsVbXsBW1YwKeD","sequencer":"0065C49DAE0659F32C"},"request-id":"VZYRK3SRJCJ1HN4T","requester":"933561452000","source-ip-address":"13.53.104.245","reason":"PutObject"}}
# lambda_handler(event, dynamodb_table_name, "")
