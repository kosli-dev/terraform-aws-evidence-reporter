data "aws_iam_policy_document" "s3_read" {
  statement {
    sid    = "S3Read"
    effect = "Allow"
    actions = [
      "s3:ListObjects",
      "s3:ListBucket",
      "S3:GetObject"
    ]
    resources = [
      "arn:aws:s3:::${var.ecs_exec_log_bucket_name}/*",
      "arn:aws:s3:::${var.ecs_exec_log_bucket_name}"
    ]
  }
}

data "aws_iam_policy_document" "ecs_read" {
  statement {
    sid    = "ECSRead"
    effect = "Allow"
    actions = [
      "ecs:DescribeTasks"
    ]
    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "kms_read" {
  statement {
    sid = "KMS"
    actions = [
      "kms:GenerateDataKey",
      "kms:Decrypt"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "cloudtrail_read" {
  statement {
    sid = "Cloudtrail"
    actions = [
      "cloudtrail:LookupEvents"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "assume_role_sso" {
  statement {
    sid = "assumeRoleSSO"
    actions = [
      "sts:AssumeRole"
    ]
    resources = [var.dynamodb_role_arn]
  }
}

data "aws_iam_policy_document" "logs" {
  statement {
    sid = "Logs"
    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogStream",
      "logs:CreateLogGroup"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    sid    = "Assume"
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}
