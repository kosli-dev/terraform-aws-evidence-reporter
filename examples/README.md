In order to deploy the evidence reporter module, you will need to do the following:

1. Set up Kolsi API token:
  - Log in to the https://app.kosli.com/, go to your profile, copy the `API Key` value.
  - Go to the AWS console -> Systems Manager service -> Parameter Store -> Create parameter. For the parameter name use `kosli_api_token` (it is also possible to set any other parameter name, but in this case you have to set `kosli_api_token_ssm_parameter_name` terraform module parameter), `Type` - `SecureString`, in the `Value` field paste API Key copied on the previous step.

2. Install Terraform: If you haven't already, you'll need to install Terraform on your local machine. You can download Terraform from the official website: https://www.terraform.io/downloads.html

3. Configure your AWS credentials: Terraform needs access to your AWS account to be able to manage your resources. You can set up your AWS credentials by following the instructions in the AWS documentation: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

4. Create a Terraform configuration: In order to use the evidence reporter module, you'll need to create a Terraform configuration. Here is the configuration [example](./examples).

5. Initialize and run Terraform: Once you've created your Terraform configuration, you'll need to initialize Terraform by running the `terraform init` command in the same directory as your configuration files. This will download the necessary modules and providers for your configuration. Then, you can run the `terraform apply` command to apply your configuration.

6. To check evidence reporter logs you can go to the AWS console -> Lambda service -> choose your lambda reporter function -> Monitor tab -> Logs tab.
