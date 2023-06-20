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
