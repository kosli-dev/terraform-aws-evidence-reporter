module "identity_reporter_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.identity_reporter_name
  description   = "Send identity evidence to the Kosli app"
  handler       = "main_ir.lambda_handler"
  runtime       = "python3.11"

  create_package = false
  publish        = true

  local_existing_package   = data.null_data_source.downloaded_package.outputs["filename"]
  recreate_missing_package = var.recreate_missing_package

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.ecs_read.json

  timeout     = 30
  memory_size = 128
  create_role = true
  role_name   = var.identity_reporter_name

  environment_variables = {
    KOSLI_HOST                       = var.kosli_host
    KOSLI_API_TOKEN                  = data.aws_ssm_parameter.kosli_api_token.value
    KOSLI_ORG                        = var.kosli_org_name
    KOSLI_AUDIT_TRAIL_NAME           = var.kosli_audit_trail_name
    KOSLI_STEP_NAME_USER_IDENTITY    = "user-identity"
    KOSLI_STEP_NAME_SERVICE_IDENTITY = "service-identity"
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

# IAM
resource "aws_cloudwatch_event_target" "ecs_exec_session_started" {
  arn       = module.identity_reporter_lambda.lambda_function_arn
  rule      = aws_cloudwatch_event_rule.ecs_exec_session_started.name
  target_id = "${var.identity_reporter_name}-ecs-exec-session-started"
}
