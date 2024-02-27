# Introduction

## Deployment

Create a CloudFormationStackManager role with the following policies attached:

- AmazonECS_FullAccess
- AmazonElastiCacheFullAccess
- AmazonRDSFullAccess
- AmazonS3FullAccess
- AmazonVPCFullAccess
- AmazonLambda_FullAccess
- IAMFullAccess
- SecretsManagerReadWrite
- CustomLogPolicy

The custom log policy needs to look like this -- note the __NOTE__
below, this is almost certainly too permissive:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:PutRetentionPolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

__NOTE__: these are almost certainly too permissive. It is recommended
that this be reduced to the least permissive set of permissions.

Next, if you plan to launch the cloudformation from the aws cli, then you
need to add your IAM user ARN to the CloudFormationStackManager role trust
relationship configuration:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudformation.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam:1231231092893:user/<youruser>"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## Create DNS and Route 53 hosted zone

## Create SSL/TSL Certificate

## launch the CloudFormation stack

### create a json params file with the required arguments and any other optional arguments

```json
[
  {
    "ParameterKey": "DBName",
    "ParameterValue": "yeastregulatorydb"
  },
  {
    "ParameterKey": "DjangoAppImage",
    "ParameterValue": "040367161929.dkr.ecr.us-east-2.amazonaws.com/django-stack:latest"
  },
  {
    "ParameterKey": "EnvFilePath",
    "ParameterValue": "s3://yeastregulatorydb-strides-tmp/.env"
  },
  {
    "ParameterKey": "FlowerHostHeader",
    "ParameterValue": "flower.yeastregulatorydb.com"
  },
  {
    "ParameterKey": "HostedZone",
    "ParameterValue": "Z046780412JUUGA0O4T7"
  },
  {
    "ParameterKey": "PostgresPassword",
    "ParameterValue": "yourpassword"
  },
  {
    "ParameterKey": "SSLCertificateArn",
    "ParameterValue": "arn:aws:acm:us-east-2:040367161929:certificate/63b33893-d593-4ae0-8f34-c09b2ee96cad"
  }
]
```

### launch the stack

Note the `file://` prefix for the template-body and parameters file paths.
Note that for this template, since IAM roles are created, the
`CAPABILITY_NAMED_IAM` capability is required.

```bash
#/usr/bin/env bash

aws cloudformation create-stack \
   --profile chasem \
  --stack-name djangostackapp-tester-2 \
  --template-body file:///home/oguzkhan/code/yeastregulatorydbstack/yeastregulatorydbstack/template_tester.txt \
  --parameters file:///home/oguzkhan/code/yeastregulatorydbstack/params.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --role-arn arn:aws:iam::040367161929:role/CloudFormationStackManager

```

### CDK notes

To deploy using CDK, you'll need to install the CDK CLI, figure out whether
you need SSO or you can use your current IAM role, and then 'bootstrap' an
environment which CDK can use to build your stacks. Follow the instructions
here:

https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_auth

but note that I had to contact AWS support to get some help -- these instructions
are vague. Here is some advice:

1. you may not need to use SSO. Try doing this:

```bash
aws sts get-caller-identity --profile <your_profile>
```

if you normally do not typically provide the `--profile <your_profile>` part
in other aws cli cmds, then you use the default profile and it is not necessary.

If you get a return from that cmd, then you are already signed in and you do
not need to worry about SSO. Continue on to the boostrap instructions.
__Note the account number -- you'll need that below__.

1. bootstrap your environment

```bash
cdk bootstrap aws://123456789012/us-east-2
```

where `123456789012` is your account number and `us-west-2` is your region.