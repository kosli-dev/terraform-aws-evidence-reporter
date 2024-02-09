import boto3


def prepare_kosli_trail_name(principal_id):
    principal_id_split = principal_id.split(":")
    prefix = principal_id_split[0]
    username = principal_id_split[1].split("@")[0]
    username = username.replace("@", "_")
    kosli_trail_name = f"{prefix}_{username}"

    return kosli_trail_name

def dynamodb_find_session_events(table_name, requester_email, account_id):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)


    print(table_name, requester_email, account_id)

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

def dynamodb_delete_session_events(table_name, events):
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