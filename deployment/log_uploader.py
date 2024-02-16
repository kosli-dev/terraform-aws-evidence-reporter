import os
import re
import json
import subprocess
import boto3
import time
import sys
from utility import dynamodb_find_session_events
from utility import dynamodb_get_session_timestamp


aws_account_id = os.environ.get("AWS_ACCOUNT_ID", "")
aws_region_sso = os.environ.get("AWS_REGION_SSO", "")
kosli_flow_name = os.environ.get("KOSLI_FLOW_NAME", "")
log_bucket_name = os.environ.get("LOG_BUCKET_NAME", "")
ecs_exec_event_wait_timeout = os.environ.get("ECS_EXEC_EVENT_WAIT_TIMEOUT", 300)
dynamodb_role_arn = os.environ.get("DYNAMODB_ROLE_ARN", "")
dynamodb_table_name = os.environ.get("DYNAMODB_TABLE_NAME", "")

def get_ecs_exec_event_principal_id(ecs_exec_session_id):
    client = boto3.client('cloudtrail')
    principal_id = ''
    ecs_exec_event_wait_count = 0
    while principal_id == '' and ecs_exec_event_wait_count < ecs_exec_event_wait_timeout:
        time.sleep(10)
        ecs_exec_event_wait_count += 10
        response = client.lookup_events(
            LookupAttributes=[{'AttributeKey': 'EventName', 'AttributeValue': 'ExecuteCommand'}]
        )
        events = response.get('Events')
        for event in events:
            event_message = json.loads(event['CloudTrailEvent'])
            response_elements = event_message.get('responseElements')
            if response_elements and response_elements.get('session').get('sessionId') == ecs_exec_session_id:
                principal_id = event_message['userIdentity']['principalId']
                break
        print(f'Waiting 10 sec more for the ECS exec event with the sessionId={ecs_exec_session_id} to apear in the Cloudtrail...', file=sys.stderr)
    if principal_id == '':
        print(f'Something went wrong, can\'t get ECS exec event with the sessionId={ecs_exec_session_id}.', file=sys.stderr)
        return None
    else:
        print(f'Done. Current ECS exec event sessionId is {ecs_exec_session_id}.', file=sys.stderr)
        return principal_id

def lambda_handler(event, context):
    try:
        # Extract S3 object key from the event data
        s3_object_key = event['detail']['object']['key']

        # Get ECS session id by extracting it from the S3 object key
        ecs_exec_session_id = s3_object_key.split('/')[-1].split('.log')[0]
        print(f'ECS_EXEC_SESSION_ID is {ecs_exec_session_id}')

        # Download the log file from S3
        s3_client = boto3.client('s3')
        local_log_file_path = f'/tmp/{ecs_exec_session_id}.log'
        s3_client.download_file(log_bucket_name, s3_object_key, local_log_file_path)

        print('Getting principal id of the current ECS exec session...')
        ecs_exec_principal_id = get_ecs_exec_event_principal_id(ecs_exec_session_id) 
        ecs_exec_user_name = ecs_exec_principal_id.split(":", 1)[1]

        sso_session_timestamp = dynamodb_get_session_timestamp(ecs_exec_user_name,
                                                               dynamodb_role_arn,
                                                               dynamodb_table_name,
                                                               aws_account_id,
                                                               aws_region_sso)

        # Create Kosli trail (if it is already exists, it will just add a report event to the existing trail)
        kosli_trail_name = str(sso_session_timestamp) + '-' + ecs_exec_user_name.split("@")[0]
        print(f'Creating Kosli trail {kosli_trail_name} within {kosli_flow_name} flow.', file=sys.stderr)

        kosli_client = subprocess.run(['./kosli', 'begin', 'trail', kosli_trail_name,
                                                '--template-file=evidence-template.yml',
                                                f'--flow={kosli_flow_name}'])

        # Upload the log file to the Kosli
        print('Uploading ECS exec log file to the Kosli...', file=sys.stderr)
        subprocess.run(['./kosli', 'attest', 'generic', 
                         f'--attachments={local_log_file_path}',
                         f'--flow={kosli_flow_name}', 
                         f'--trail={kosli_trail_name}',
                         '--name=command-logs'])

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
