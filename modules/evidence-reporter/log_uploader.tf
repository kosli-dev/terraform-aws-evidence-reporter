module "log_uploader_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name  = var.log_uploader_name
  description    = "Send evidence reports to the Kosli app"
  handler        = "log_uploader.lambda_handler"
  runtime        = "python3.11"
  create_package = false
  publish        = true

  local_existing_package = data.null_data_source.downloaded_package.outputs["filename"]

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.log_uploader_combined.json

  maximum_retry_attempts = 0
  timeout                = 300
  memory_size            = 128
  create_role            = true
  role_name              = var.log_uploader_name

  recreate_missing_package = var.recreate_missing_package

  environment_variables = {
    AWS_ACCOUNT_ID      = data.aws_caller_identity.current.account_id
    AWS_REGION_SSO      = var.aws_region_sso
    KOSLI_HOST          = var.kosli_host
    KOSLI_API_TOKEN     = data.aws_ssm_parameter.kosli_api_token.value
    KOSLI_ORG           = var.kosli_org_name
    KOSLI_FLOW_NAME     = var.kosli_flow_name
    LOG_BUCKET_NAME     = var.ecs_exec_log_bucket_name
    DYNAMODB_ROLE_ARN   = var.dynamodb_role_arn
    DYNAMODB_TABLE_NAME = var.dynamodb_table_name
  }

  allowed_triggers = {
    AllowExecutionFromCloudWatchS3 = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.s3_object_created.arn
    }
  }

  cloudwatch_logs_retention_in_days = var.cloudwatch_logs_retention_in_days

  tags = var.tags
}

# Eventbridge trigger
resource "aws_cloudwatch_event_rule" "s3_object_created" {
  name        = "${var.log_uploader_name}-s3-object-created"
  description = "S3 object has been created"

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"],
    detail = {
      bucket = {
        name = [var.ecs_exec_log_bucket_name]
      }
    }
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_target" "s3_object_created" {
  arn       = module.log_uploader_lambda.lambda_function_arn
  rule      = aws_cloudwatch_event_rule.s3_object_created.name
  target_id = "${var.log_uploader_name}-s3-object-created"
}

# IAM
data "aws_iam_policy_document" "log_uploader_combined" {
  source_policy_documents = concat(
    [data.aws_iam_policy_document.kms_read.json],
    [data.aws_iam_policy_document.s3_read.json],
    [data.aws_iam_policy_document.cloudtrail_read.json],
    [data.aws_iam_policy_document.assume_role_sso.json]
  )
}
