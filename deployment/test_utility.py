import pytest
from unittest.mock import patch, MagicMock
import utility

@pytest.fixture
def mock_table():
    mock = MagicMock()
    mock.scan.return_value = {'Items': [{'requester_email': 'user@example.com', 'account_id': '123', 'timestamp': '111'}]}
    return mock

def test_dynamodb_find_session_events(mock_table):
    items = utility.dynamodb_find_session_events(mock_table, 'user@example.com', '123')
    assert items == [{'requester_email': 'user@example.com', 'account_id': '123', 'timestamp': '111'}]

@patch('utility.boto3.resource')
def test_dynamodb_delete_session_events(mock_boto3_resource):
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    events = [{'timestamp': '111'}]
    utility.dynamodb_delete_session_events('table_name', events)
    mock_table.delete_item.assert_called_with(Key={'timestamp': '111'})

@patch('utility.boto3.resource')
@patch('utility.boto3.client')
def test_dynamodb_get_session_event(mock_boto3_client, mock_boto3_resource):
    # Mock STS assume_role
    mock_sts = MagicMock()
    mock_sts.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'id',
            'SecretAccessKey': 'key',
            'SessionToken': 'token'
        }
    }
    mock_boto3_client.return_value = mock_sts
    # Mock DynamoDB resource and table
    mock_table = MagicMock()
    mock_table.scan.return_value = {'Items': [{'requester_email': 'user@example.com', 'account_id': '123', 'timestamp': '111'}]}
    mock_boto3_resource.return_value.Table.return_value = mock_table
    # Patch pop to return the last item
    with patch('utility.dynamodb_find_session_events', return_value=[{'requester_email': 'user@example.com', 'account_id': '123', 'timestamp': '111'}]):
        event = utility.dynamodb_get_session_event('user@example.com', 'role_arn', 'table', '123', 'us-west-2')
        assert event['timestamp'] == '111' 