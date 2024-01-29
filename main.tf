module "evidence_reporter" {
  source = "./modules/evidence-reporter"
  identity_reporter_name = var.identity_reporter_name
  log_uploader_name = var.log_uploader_name
  kosli_host = var.kosli_host
  kosli_org_name = var.kosli_org_name
  kosli_flow_name = var.kosli_flow_name
  ecs_exec_log_bucket_name = var.ecs_exec_log_bucket_name
  recreate_missing_package = var.recreate_missing_package
  cloudwatch_logs_retention_in_days = var.cloudwatch_logs_retention_in_days
  tags = var.tags
}

module "session_reporter" {
  source = "./modules/session-reporter"
}