import boto3


def deploy_stack(stack_name, template_body):
    """Deploy or update CloudFormation stack."""
    cf_client = boto3.client("cloudformation")

    try:
        validate_response = cf_client.validate_template(TemplateBody=template_body)
        print("Template is valid.")
        print(
            validate_response
        )  # This will print details of the validation, including capabilities required, etc.
    except cf_client.exceptions.ValidationError as e:
        print("Template is invalid.")
        print(e)
    try:
        cf_client.describe_stacks(StackName=stack_name)
        print(f"Updating stack {stack_name}...")
        response = cf_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        )
        print(f"Stack update initiated: {response['StackId']}")
    except cf_client.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Creating stack {stack_name}...")
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            )
            print(f"Stack creation initiated: {response['StackId']}")
        else:
            raise


if __name__ == "__main__":
    stack_name = "YeastRegulatoryDBStack"
    template_body = create_template(
        resource_list=[
            vpc_subnets_routetables_networkcon.get_resources(),
            rds_redis_ec2.get_resources(),
            ecs_fargate.get_resources(),
            alb.get_resources(),
        ],
        output_list=[
            vpc_subnets_routetables_networkcon.get_outputs(),
            rds_redis_ec2.get_outputs(),
            ecs_fargate.get_outputs(),
            alb.get_outputs(),
        ],
    )
    deploy_stack(stack_name, template_body)
