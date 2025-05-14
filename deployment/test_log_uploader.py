import pytest
from unittest.mock import patch, MagicMock
import log_uploader

@pytest.fixture
def sample_event():
    return {
        'detail': {
            'object': {'key': 'logs/sess-123.log'}
        }
    }

@patch('log_uploader.dynamodb_get_session_event')
@patch('log_uploader.get_ecs_exec_event_principal_id')
@patch('log_uploader.subprocess.run')
@patch('log_uploader.boto3.client')
def test_lambda_handler_success(mock_boto3_client, mock_run, mock_get_principal_id, mock_get_session_event, sample_event):
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3
    mock_s3.download_file.return_value = None
    mock_get_principal_id.return_value = 'user:foo@example.com'
    mock_get_session_event.return_value = {
        'timestamp': 1234567890,
        'requester_email': 'foo@example.com',
        'approver_email': 'bar@example.com',
        'role_name': 'role',
        'permission_duration': 3600,
        'account_id': '123',
        'reason': 'test'
    }
    mock_run.return_value = MagicMock()
    context = MagicMock()
    result = log_uploader.lambda_handler(sample_event, context)
    assert result['statusCode'] == 200
    assert 'Handler executed successfully' in result['body']

@patch('log_uploader.get_ecs_exec_event_principal_id', side_effect=Exception('fail'))
def test_lambda_handler_error(mock_get_principal_id, sample_event):
    context = MagicMock()
    result = log_uploader.lambda_handler(sample_event, context)
    assert result['statusCode'] == 500
    assert 'Handler encountered an error' in result['body'] 