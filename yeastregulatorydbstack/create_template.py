from yeastregulatorydbstack.resources import (
    alb,
    ecs_fargate,
    lambda_functions,
    rds_redis_ec2,
    security_groups,
    vpc_subnets_routetables_networkcon,
)

HEADER = (
    """
AWSTemplateFormatVersion: '2010-09-09'
Description: CloudFormation template for PostgreSQL RDS, ElastiCache Redis, """
    + "EC2 and a ECS/Fargate cluster for a django app complete with VPC, "
    + "subnets, security groups, and IAM roles."
)


def create_template(
    parameter_list: list, resource_list: list, output_list: list
) -> str:
    """Create a CloudFormation template."""
    template = HEADER + "\n\nParameters:\n"
    for parameter in parameter_list:
        template += parameter
    template += "\nResources:\n"
    for resource in resource_list:
        template += resource
    template += "\nOutputs:\n"
    for output in output_list:
        template += output
    return template


if __name__ == "__main__":
    template_body = create_template(
        parameter_list=[
            vpc_subnets_routetables_networkcon.get_parameters(),
            security_groups.get_parameters(),
            lambda_functions.get_parameters(),
            rds_redis_ec2.get_parameters(),
            ecs_fargate.get_parameters(),
            alb.get_parameters(),
        ],
        resource_list=[
            vpc_subnets_routetables_networkcon.get_resources(),
            security_groups.get_resources(),
            lambda_functions.get_resources(),
            rds_redis_ec2.get_resources(),
            ecs_fargate.get_resources(),
            alb.get_resources(),
        ],
        output_list=[
            vpc_subnets_routetables_networkcon.get_outputs(),
            security_groups.get_outputs(),
            lambda_functions.get_outputs(),
            rds_redis_ec2.get_outputs(),
            ecs_fargate.get_outputs(),
            alb.get_outputs(),
        ],
    )
    print(template_body)
