## Kosli Evidence Reporter module
This repository contains a set of modules in the [modules folder](https://github.com/kosli-dev/terraform-aws-evidence-reporter/tree/main/modules) for deploying Kosli Evidence Reporter. Kosli Evidence Reporter is an automation designed to send evidence reports to Kosli. Currently, it only works for ECS exec sessions. Once the ECS exec session is finished, three types of reports are sent to Kosli:
- a log file (containing commands run using ECS exec within the container)
- user-identity report (indicating the identity of the user who started the ECS exec session)
- service-identity report (the name of the accessed ECS service)
This module assumes that you are using [SSO-elevator](https://github.com/fivexl/terraform-aws-sso-elevator) - a solution for granting temporary SSO access to AWS accounts. Kosli Evidence Reporter groups the evidence into separate trails by access grant. For example, if a user gets temporary AWS access through SSO-elevator, all the ECS exec session evidence reported while this access is valid will be grouped into a single Kosli trail with the name in the format `<SSO-session-grant-timestamp>-<user-name>`.
The repository contains two modules - [evidence-reporter](https://github.com/kosli-dev/terraform-aws-evidence-reporter/tree/main/modules/evidence-reporter) and [session-saver](https://github.com/kosli-dev/terraform-aws-evidence-reporter/tree/main/modules/session-saver). Session-saver is supposed to be deployed to the SSO AWS account, where SSO-elevator resides. It captures access grant and revoke events and accordingly manages these event records in DynamoDB. Evidence-reporter is supposed to be deployed to the workload AWS account. Based on access event records in DynamoDB, it groups and sends the evidence reports to Kosli.

## Set up Kolsi API token
1. Log in to the https://app.kosli.com/, go to your profile, copy the `API Key` value.
2. Store the Kosli API key value in an AWS SSM parameter (SecureString type). By default, the Lambda Reporter will search for the `kosli_api_token` SSM parameter name, but it is also possible to set custom parameter name (use `kosli_api_token_ssm_parameter_name` variable).

## Usage
1. Ensure that ECS Exec logging is enabled for your ECS clusters and is [configured](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html) to save log files to an S3 bucket. Let's assume the ECS Exec log bucket name is `my-ecs-log-bucket`.

2. Create a [Flow](https://docs.kosli.com/client_reference/kosli_create_flow/) in your Kosli organisation.

3. Deploy the session-saver module to the SSO account (AWS account where SSO-elevator resides):
```
module "session-saver" {
  source                   = "kosli-dev/evidence-reporter/aws//modules/session-saver"
  version                  = "0.3.4"
  sso_elevator_bucket_name = "sso-elevator-audit-d3076b3d08b642a7a9be737dee53e726"
}
```

4. Deploy the evidence-reporter module to the workload account:
```
module "evidence-reporter" {
  source  = "kosli-dev/evidence-reporter/aws//modules/evidence-reporter"
  version = "0.3.4"

  kosli_org_name           = "kosli"
  ecs_exec_log_bucket_name = "my-ecs-log-bucket"
  kosli_flow_name          = "staging-access"
  dynamodb_role_arn        = "arn:aws:iam::12345678912:role/evidence-reporter-cross-acount"
}
```

4. Run the [ecs exec](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecs/execute-command.html) command.

5. After ECS exec session is closed, check the `staging-access` Flow in your Kosli organisation. A new Trail should appear with the ID in format `<SSO_session_grant_timestamp>-<username>`. The Trail should contain three Trail Attestations - `command-logs`, `service-identity` and `user-identity`. 
