data "aws_iam_policy_document" "s3_read" {
  statement {
    sid    = "S3Read"
    effect = "Allow"
    actions = [
      "s3:ListObjects",
      "s3:ListBucket",
      "s3:GetObject"
    ]
    resources = [
      "arn:aws:s3:::${var.sso_elevator_bucket_name}/*",
      "arn:aws:s3:::${var.sso_elevator_bucket_name}"
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_write" {
  statement {
    sid    = "DynamoDBWrite"
    effect = "Allow"
    actions = [
      "dynamodb:Get*",
      "dynamodb:Describe*",
      "dynamodb:List*",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan"
    ]
    resources = [
      aws_dynamodb_table.this.arn
    ]
  }
}

data "aws_iam_policy_document" "combined" {
  source_policy_documents = concat(
    [data.aws_iam_policy_document.s3_read.json],
    [data.aws_iam_policy_document.dynamodb_write.json]
  )
}

# Role is used by identity-reporter and log uploader to access DynamoDB
resource "aws_iam_role" "dynamodb_org_full_access" {
  name = "dynamodb_org_full_access"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "*"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {
          "StringEquals" : {
            "aws:PrincipalOrgID" : "${data.aws_organizations_organization.org.id}"
          }
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy_attachment" "dynamodb_org_full_access" {
  name       = "OrganizationDynamoDBFullAccess"
  roles      = [aws_iam_role.dynamodb_org_full_access.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}
