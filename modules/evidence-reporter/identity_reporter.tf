module "identity_reporter_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.identity_reporter_name
  description   = "Send identity evidence to the Kosli app"
  handler       = "identity_reporter.lambda_handler"
  runtime       = "python3.11"

  create_package = false
  publish        = true

  local_existing_package   = data.null_data_source.downloaded_package.outputs["filename"]
  recreate_missing_package = var.recreate_missing_package

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.identity_reporter_combined.json

  maximum_retry_attempts = 0
  timeout                = 30
  memory_size            = 128
  create_role            = true
  role_name              = var.identity_reporter_name

  environment_variables = {
    AWS_ACCOUNT_ID      = data.aws_caller_identity.current.account_id
    AWS_REGION_SSO      = var.aws_region_sso
    KOSLI_HOST          = var.kosli_host
    KOSLI_API_TOKEN     = data.aws_ssm_parameter.kosli_api_token.value
    KOSLI_ORG           = var.kosli_org_name
    KOSLI_FLOW_NAME     = var.kosli_flow_name
    DYNAMODB_ROLE_ARN   = var.dynamodb_role_arn
    DYNAMODB_TABLE_NAME = var.dynamodb_table_name
  }

  allowed_triggers = {
    AllowExecutionFromCloudWatchECS = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.ecs_exec_session_started.arn
    }
  }

  cloudwatch_logs_retention_in_days = var.cloudwatch_logs_retention_in_days

  tags = var.tags
}

# Eventbridge trigger
resource "aws_cloudwatch_event_rule" "ecs_exec_session_started" {
  name        = "${var.identity_reporter_name}-ecs-exec-session-started"
  description = "ECS exec session is started"

  event_pattern = jsonencode({
    source      = ["aws.ecs"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventName = ["ExecuteCommand"],
      responseElements = {
        session = {
          sessionId = [{
            prefix = ""
          }]
        }
      }
    }
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_target" "ecs_exec_session_started" {
  arn       = module.identity_reporter_lambda.lambda_function_arn
  rule      = aws_cloudwatch_event_rule.ecs_exec_session_started.name
  target_id = "${var.identity_reporter_name}-ecs-exec-session-started"
}

# IAM
data "aws_iam_policy_document" "identity_reporter_combined" {
  source_policy_documents = concat(
    [data.aws_iam_policy_document.ecs_read.json],
    [data.aws_iam_policy_document.assume_role_sso.json]
  )
}
