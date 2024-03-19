import boto3
import json
import subprocess
import sys
import os
from utility import dynamodb_find_session_events
from utility import dynamodb_get_session_event


kosli_flow_name = os.environ.get("KOSLI_FLOW_NAME", "")
aws_account_id = os.environ.get("AWS_ACCOUNT_ID", "")
aws_region_sso = os.environ.get("AWS_REGION_SSO", "")
dynamodb_role_arn = os.environ.get("DYNAMODB_ROLE_ARN", "")
dynamodb_table_name = os.environ.get("DYNAMODB_TABLE_NAME", "")


def describe_ecs_task(cluster, task_arn):
    ecs_client = boto3.client('ecs')
    response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn])
    return response

def lambda_handler(event, context):
    try:
        ecs_exec_session_id = event['detail']['responseElements']['session']['sessionId']
        print(f"ECS_EXEC_SESSION_ID is {ecs_exec_session_id}", file=sys.stderr)

        ecs_exec_principal_id = event['detail']['userIdentity']['principalId']
        ecs_exec_user_name = ecs_exec_principal_id.split(":", 1)[1]

        sso_session_event = dynamodb_get_session_event(ecs_exec_user_name,
                                                           dynamodb_role_arn,
                                                           dynamodb_table_name,
                                                           aws_account_id,
                                                           aws_region_sso)
        sso_session_timestamp = int(sso_session_event['timestamp'])

        # Create Kosli trail (if it is already exists, it will just add a report event to the existing trail)
        kosli_trail_name = str(sso_session_timestamp) + '-' + ecs_exec_user_name.split("@")[0]
        print(f'Creating Kosli trail {ecs_exec_principal_id} within {kosli_flow_name} flow.')
    
        kosli_client = subprocess.check_output(['./kosli', 'begin', 'trail', kosli_trail_name,
                                                '--template-file=evidence-template.yml',
                                                f'--flow={kosli_flow_name}'])

        # Get and report ECS exec session user identity (ARN of the IAM role that initiated the session)
        ecs_exec_user_identity = event['detail']['userIdentity']['arn']
        with open('/tmp/user-identity.json', 'w') as user_identity_file:
            json.dump({"ecs_exec_role_arn": ecs_exec_user_identity}, user_identity_file)

        print("Reporting ECS exec user identity to the Kosli...", file=sys.stderr)
        subprocess.run(['./kosli', 'attest', 'generic', 
                        f'--attachments=/tmp/user-identity.json',
                        f'--flow={kosli_flow_name}', 
                        f'--trail={kosli_trail_name}',
                        '--name=user-identity',
                        '--user-data=/tmp/user-identity.json'])

        # Get and report ECS exec session service identity
        json_identity_data = {
            'requester_email': sso_session_event['requester_email'],
            'approver_email': sso_session_event['approver_email'],
            'role_name': sso_session_event['role_name'],
            'permission_duration': sso_session_event['permission_duration'],
            'account_id': sso_session_event['account_id'],
            'reason': sso_session_event['reason']
        }

        with open('/tmp/service-identity.json', 'w') as service_identity_file:
            json.dump(json_identity_data, service_identity_file)

        print("Reporting ECS exec service identity to the Kosli...", file=sys.stderr)
        subprocess.run(['./kosli', 'attest', 'generic',
                        f'--attachments=/tmp/service-identity.json',
                        f'--flow={kosli_flow_name}', 
                        f'--trail={kosli_trail_name}',
                        '--name=service-identity',
                        '--user-data=/tmp/service-identity.json'])

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
