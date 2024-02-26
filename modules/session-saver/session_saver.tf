module "session_saver_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.session_saver_name
  description   = "Update SSO session records in DynamoDB"
  handler       = "session_saver.lambda_handler"
  runtime       = "python3.11"

  create_package           = true
  publish                  = true
  source_path              = "${path.module}/deployment"
  recreate_missing_package = var.recreate_missing_package

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.combined.json

  maximum_retry_attempts = 0
  timeout                = 30
  memory_size            = 128
  create_role            = true
  role_name              = var.session_saver_name

  environment_variables = {
    SSO_ELEVATOR_AUDIT_BUCKET_NAME = var.sso_elevator_bucket_name
    DYNAMODB_TABLE_NAME            = aws_dynamodb_table.this.id
  }

  allowed_triggers = {
    AllowExecutionFromCloudWatchECS = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.s3_object_created.arn
    }
  }

  cloudwatch_logs_retention_in_days = var.cloudwatch_logs_retention_in_days

  tags = var.tags
}

# Eventbridge trigger
resource "aws_cloudwatch_event_rule" "s3_object_created" {
  name        = "${var.session_saver_name}-sso-session-event"
  description = "SSO session event log file uploaded to S3"

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"],
    detail = {
      bucket = {
        name = [var.sso_elevator_bucket_name]
      }
    }
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_target" "s3_object_created" {
  arn       = module.session_saver_lambda.lambda_function_arn
  rule      = aws_cloudwatch_event_rule.s3_object_created.name
  target_id = "${var.session_saver_name}-s3-object-created"
}
