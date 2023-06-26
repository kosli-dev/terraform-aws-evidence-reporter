provider "aws" {
  region = local.region

  # Make it faster by skipping something
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

locals {
  reporter_name = "reporter-${random_pet.this.id}"
  region        = "eu-central-1"
}

data "aws_caller_identity" "current" {}

data "aws_canonical_user_id" "current" {}

resource "random_pet" "this" {
  length = 4
}

module "evidence-reporter" {
  source  = "kosli-dev/ecs-evidence-reporter/aws"
  version = "0.0.1"

  kosli_api_token_ssm_parameter_name = "/infra/kosli/api_token"

  kosli_cli_version      = "2.5.0"
  kosli_org_name         = "my-company"
  kosli_host             = "https://app.kosli.com/"
  kosli_audit_trail_name = "staging-access"

  log_uploader_name       = "log-uploader-${local.reporter_name}"
  user_data_reporter_name = "user-data-reporter-${local.reporter_name}"

  ecs_exec_log_bucket_name = "my-ecs-log-bucket"

  tags = module.tags.result
}

module "tags" {
  source            = "fivexl/tag-generator/aws"
  version           = "2.0.0"
  terraform_managed = "1"
  environment_name  = "staging"
  data_owner        = "my-company"
}
