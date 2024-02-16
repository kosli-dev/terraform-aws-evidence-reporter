import boto3


def dynamodb_find_session_events(table, requester_email, account_id):
    response = table.scan(
        FilterExpression=f'#attribute1_name = :attr1_val AND #attribute2_name = :attr2_val',
        ExpressionAttributeNames={
            '#attribute1_name': 'requester_email',
            '#attribute2_name': 'account_id'
        },
        ExpressionAttributeValues={
            ':attr1_val': requester_email,
            ':attr2_val': account_id
        }
    )

    return response['Items']

def dynamodb_delete_session_events(table, events):
    if events:
        print("Matching events found. Deleting...")

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        for event in events:
            response = table.delete_item(
                Key={
                    'timestamp': event['timestamp']
                }
            )
            print("Deleted event:", event)
    else:
        print("No events found containing both attributes:",
              'requester_email', "with value:", session_event_requester_email,
              "and", 'account_id', "with value:", session_event_account_id)

def dynamodb_get_session_timestamp(ecs_exec_user_name, dynamodb_role_arn, dynamodb_table_name, aws_account_id, aws_region_sso):
    # Get SSO session parameters from
    sts_client = boto3.client('sts')
    sts_session = sts_client.assume_role(RoleArn=dynamodb_role_arn, RoleSessionName=f'reporter-dynamodb-session-{aws_account_id}')
    KEY_ID = sts_session['Credentials']['AccessKeyId']
    ACCESS_KEY = sts_session['Credentials']['SecretAccessKey']
    TOKEN = sts_session['Credentials']['SessionToken']
    dynamodb = boto3.resource('dynamodb',
                              region_name=aws_region_sso, 
                              aws_access_key_id=KEY_ID, 
                              aws_secret_access_key=ACCESS_KEY, 
                              aws_session_token=TOKEN)
    dynamodb_table = dynamodb.Table(dynamodb_table_name)

    # There could be multiple sessions, getting the latest
    sso_session_event = dynamodb_find_session_events(dynamodb_table, 
                                                     ecs_exec_user_name, 
                                                     aws_account_id).pop()
    sso_session_timestamp = int(sso_session_event['timestamp'])
    
    return sso_session_timestamp