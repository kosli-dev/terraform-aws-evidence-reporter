import pytest
from unittest.mock import patch, MagicMock
import session_saver

@pytest.fixture
def sample_event_grant():
    return {
        'detail': {
            'object': {'key': 'logs/session-grant.json'}
        }
    }

@pytest.fixture
def sample_event_revoke():
    return {
        'detail': {
            'object': {'key': 'logs/session-revoke.json'}
        }
    }

@patch('builtins.open')
@patch('session_saver.boto3.resource')
@patch('session_saver.boto3.client')
def test_lambda_handler_grant(mock_boto3_client, mock_boto3_resource, mock_open, sample_event_grant):
    # Mock S3 download
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3
    mock_s3.download_file.return_value = None
    # Mock file read
    mock_open.return_value.read.return_value = '{"timestamp": 123, "requester_email": "foo@example.com", "account_id": "123", "operation_type": "grant"}'
    # Mock DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    context = MagicMock()
    result = session_saver.lambda_handler(sample_event_grant, context)
    assert result['statusCode'] == 200
    assert 'Handler executed successfully' in result['body']

@patch('builtins.open')
@patch('session_saver.boto3.resource')
@patch('session_saver.boto3.client')
@patch('session_saver.dynamodb_find_session_events')
@patch('session_saver.dynamodb_delete_session_events')
def test_lambda_handler_revoke(mock_delete, mock_find, mock_boto3_client, mock_boto3_resource, mock_open, sample_event_revoke):
    # Mock S3 download
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3
    mock_s3.download_file.return_value = None
    # Mock file read
    mock_open.return_value.read.return_value = '{"timestamp": 123, "requester_email": "foo@example.com", "account_id": "123", "operation_type": "revoke"}'
    # Mock DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_find.return_value = [{'timestamp': 123}]
    context = MagicMock()
    result = session_saver.lambda_handler(sample_event_revoke, context)
    assert result['statusCode'] == 200
    assert 'Handler executed successfully' in result['body']

@patch('session_saver.boto3.client', side_effect=Exception('fail'))
def test_lambda_handler_error(mock_boto3_client, sample_event_grant):
    context = MagicMock()
    result = session_saver.lambda_handler(sample_event_grant, context)
    assert result['statusCode'] == 500
    assert 'Handler encountered an error' in result['body'] 