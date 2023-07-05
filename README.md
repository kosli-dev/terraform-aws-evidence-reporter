# Kosli ECS evidence Reporter
With Amazon [ECS Exec](https://aws.amazon.com/ru/blogs/containers/new-using-amazon-ecs-exec-access-your-containers-fargate-ec2/), you can directly interact with containers running on your infrastructure. The Kosli ECS Evidence Reporter Terraform module is used to deploy infrastructure for automating the sending of ECS exec reports to Kosli. Two types of reports are sent: a log file (containing commands run using ECS Exec inside the container) and a user-identity report (indicating the identity of the user who started the ECS Exec session).

## Set up Kolsi API token
1. Log in to the https://app.kosli.com/, go to your profile, copy the `API Key` value.
2. Store the Kosli API key value in an AWS SSM parameter (SecureString type). By default, the Lambda Reporter will search for the `kosli_api_token` SSM parameter name, but it is also possible to set custom parameter name (use `kosli_api_token_ssm_parameter_name` variable).

## Usage
1. Ensure that ECS Exec logging is enabled for your ECS clusters and is [configured](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html) to save log files to an S3 bucket. Let's assume the ECS Exec log bucket name is `my-ecs-log-bucket`.
2. Create an [Audit-trail](https://docs.kosli.com/kosli_overview/what_is_audit_trail/) in your Kosli organisation, for example `staging-access` with the steps `command-logs` and `user-identity`.
3. Deploy the evidence reporter module:
```
module "evidence-reporter" {
  source  = "kosli-dev/ecs-evidence-reporter/aws"
  version = "0.0.1"

  kosli_org_name           = "kosli"
  ecs_exec_log_bucket_name = "my-ecs-log-bucket"
  kosli_audit_trail_name   = "staging-access"
}
```
4. Run the [ecs exec](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecs/execute-command.html) command.
5. After ECS exec session is closed, check the `staging-access` audit-trail in your Kosli organisation. A new workflow should appear with the name of the ECS Exec session ID (ecs-execute-command-"random-id"). The workflow should contain two evidence reports - `command-logs` and `user-identity`, both are dowloadable. 
