variable "session_saver_name" {
  type        = string
  default     = "sso-session-saver"
  description = "The name of the AWS resources related to the SSO session lambda."
}

variable "sso_elevator_bucket_name" {
  type        = string
  description = "The name of S3 bucket where SSO elevator audit logs are stored."
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

# variable "kosli_cli_version" {
#   type        = string
#   description = "The Kosli cli version, should be set in format 2.7.8"
#   default     = "2.7.8"
# }

# variable "reporter_releases_host" {
#   type        = string
#   default     = "https://reporter-releases.kosli.com"
#   description = "Where to download the Reporter Lambda package."
# }