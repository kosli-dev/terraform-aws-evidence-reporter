variable "log_uploader_name" {
  type        = string
  default     = "ecs-exec-log-uploader"
  description = "The name of the AWS resources related to the log uploader lambda."
}

variable "identity_reporter_name" {
  type        = string
  default     = "ecs-exec-identity-reporter"
  description = "The name of the AWS resources related to the identity reporter lambda."
}

variable "ecs_exec_log_bucket_name" {
  type        = string
  description = "The name of S3 bucket where ECS exec logs are stored."
}

variable "kosli_host" {
  default = "https://app.kosli.com/"
  type    = string
}

variable "kosli_org_name" {
  type        = string
  description = "Kosli organisation name (the value for the cli --org parameter)."
}

variable "kosli_flow_name" {
  type        = string
  description = "Kosli flow name."
}

variable "recreate_missing_package" {
  type        = bool
  default     = true
  description = "Whether to recreate missing Lambda package if it is missing locally or not."
}

variable "tags" {
  type        = map(string)
  description = "Tags to assign to the AWS resources."
  default     = {}
}

variable "cloudwatch_logs_retention_in_days" {
  type        = number
  default     = 7
  description = "The retention period of reporter logs (days)."
}
