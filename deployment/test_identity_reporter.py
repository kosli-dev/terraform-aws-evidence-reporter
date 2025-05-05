import pytest
from unittest.mock import patch, MagicMock
import identity_reporter

@pytest.fixture
def sample_event():
    return {
        'detail': {
            'responseElements': {
                'session': {'sessionId': 'sess-123'},
                'taskArn': 'task-arn-123'
            },
            'userIdentity': {
                'principalId': 'user:foo@example.com',
                'arn': 'arn:aws:iam::123:user/foo@example.com'
            },
            'requestParameters': {
                'cluster': 'cluster-1'
            }
        }
    }

@patch('identity_reporter.dynamodb_get_session_event')
@patch('identity_reporter.describe_ecs_task')
@patch('identity_reporter.subprocess.run')
@patch('identity_reporter.subprocess.check_output')
def test_lambda_handler_success(mock_check_output, mock_run, mock_describe_ecs_task, mock_get_session_event, sample_event):
    mock_get_session_event.return_value = {
        'timestamp': 1234567890,
        'requester_email': 'foo@example.com',
        'approver_email': 'bar@example.com',
        'role_name': 'role',
        'permission_duration': 3600,
        'account_id': '123',
        'reason': 'test'
    }
    mock_describe_ecs_task.return_value = {'tasks': [{'group': 'service-group'}]}
    mock_check_output.return_value = b''
    mock_run.return_value = MagicMock()
    context = MagicMock()
    result = identity_reporter.lambda_handler(sample_event, context)
    assert result['statusCode'] == 200
    assert 'Handler executed successfully' in result['body']

@patch('identity_reporter.dynamodb_get_session_event', side_effect=Exception('fail'))
def test_lambda_handler_error(mock_get_session_event, sample_event):
    context = MagicMock()
    result = identity_reporter.lambda_handler(sample_event, context)
    assert result['statusCode'] == 500
    assert 'Handler encountered an error' in result['body'] 