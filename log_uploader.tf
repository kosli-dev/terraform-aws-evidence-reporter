module "log_uploader_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.18.0"

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.log_uploader_combined.json

  function_name = var.log_uploader_name
  description   = "Send evidence reports to the Kosli app"
  handler       = "upload-log-file.handler"
  runtime       = "provided"
  layers = [
    var.LAYER_VERSION_ARN_AWSCLI,
    var.LAYER_VERSION_ARN_BASH_UTILITIES
  ]
  source_path = [
    "${path.module}/src/bootstrap",
    "${path.module}/src/upload-log-file.sh",
    "${local.kosli_src_path}/kosli"
  ]
  timeout        = 30
  memory_size    = 512
  create_package = true
  publish        = true
  create_role    = true
  role_name      = var.log_uploader_name

  recreate_missing_package = var.recreate_missing_package

  environment_variables = {
    KOSLI_HOST             = var.kosli_host
    KOSLI_API_TOKEN        = data.aws_ssm_parameter.kosli_api_token.value
    KOSLI_ORG              = var.kosli_org_name
    KOSLI_AUDIT_TRAIL_NAME = var.kosli_audit_trail_name
    KOSLI_STEP_NAME        = "command-logs"
    LOG_BUCKET_NAME        = var.ecs_exec_log_bucket_name
  }

  allowed_triggers = {
    AllowExecutionFromCloudWatchS3 = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.s3_object_created.arn
    }
  }

  cloudwatch_logs_retention_in_days = 1

  depends_on = [
    null_resource.download_and_unzip
  ]

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
    [data.aws_iam_policy_document.s3_read.json]
  )
}
