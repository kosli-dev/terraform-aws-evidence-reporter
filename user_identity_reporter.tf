module "user_data_reporter_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.18.0"

  function_name  = var.user_data_reporter_name
  description    = "Send user data to the Kosli app"
  handler        = "report-user-identity.handler"
  runtime        = "provided"
  create_package = false
  publish        = true

  local_existing_package = data.null_data_source.downloaded_package.outputs["filename"]

  layers = [
    var.LAYER_VERSION_ARN_BASH_UTILITIES
  ]

  timeout     = 30
  memory_size = 128
  create_role = true
  role_name   = var.user_data_reporter_name

  recreate_missing_package = var.recreate_missing_package

  environment_variables = {
    KOSLI_HOST             = var.kosli_host
    KOSLI_API_TOKEN        = data.aws_ssm_parameter.kosli_api_token.value
    KOSLI_ORG              = var.kosli_org_name
    KOSLI_AUDIT_TRAIL_NAME = var.kosli_audit_trail_name
    KOSLI_STEP_NAME        = "user-identity"
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
  name        = "${var.user_data_reporter_name}-ecs-exec-session-started"
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
  arn       = module.user_data_reporter_lambda.lambda_function_arn
  rule      = aws_cloudwatch_event_rule.ecs_exec_session_started.name
  target_id = "${var.user_data_reporter_name}-ecs-exec-session-started"
}
