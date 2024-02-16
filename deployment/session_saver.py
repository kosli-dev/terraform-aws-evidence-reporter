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

        dynamodb = boto3.resource('dynamodb')
        dynamodb_table = dynamodb.Table(dynamodb_table_name)

        # Put event to the DynamoDB
        if session_operation_type == "grant":
            print('Putting the SSO event to the DynamoDB table...')
            response = dynamodb_table.put_item(Item=json.loads(log_file_content))
            print("DynamoDB PutItem succeeded")
        
        # Remove event from DynamoDB
        elif session_operation_type == "revoke":
            print('Removing the SSO event from the DynamoDB table...')
            sso_session_events = dynamodb_find_session_events(dynamodb_table, 
                                                              session_event_requester_email, 
                                                              session_event_account_id)
            dynamodb_delete_session_events(dynamodb_table, 
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
