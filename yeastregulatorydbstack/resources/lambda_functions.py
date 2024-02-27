"""
UpdateSecreteLambdaFunction and SecretUpdater function to update the DB
secret with the RDS endpoint. This is necessary because the RDS instance
endpoint is not known at the time the secret is created. This info is necessary
to use the DBProxy
"""


def get_parameters() -> str:
    return """"""


def get_resources() -> str:
    return """
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: LambdaSecretsManagerAndLogsPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                  - secretsmanager:UpdateSecret
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: '*'

  UpdateSecretLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Runtime: python3.8
      Code:
        ZipFile: |
          import json
          import boto3
          import cfnresponse

          def lambda_handler(event, context):
              try:
                  if event['RequestType'] in ['Create', 'Update']:
                      props = event['ResourceProperties']
                      secret_arn = props['SecretArn']
                      rds_endpoint = props['RDSEndpoint']

                      secrets_manager_client = boto3.client('secretsmanager')
                      current_secret_value = secrets_manager_client.get_secret_value(SecretId=secret_arn)['SecretString']
                      secret_dict = json.loads(current_secret_value)

                      secret_dict['host'] = rds_endpoint
                      secrets_manager_client.update_secret(SecretId=secret_arn, SecretString=json.dumps(secret_dict))

                  cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
              except Exception as e:
                  print(e)
                  cfnresponse.send(event, context, cfnresponse.FAILED, {})
      Timeout: 120  # Adjust the timeout based on the expected execution time

  # Custom resource to trigger Lambda function
  SecretUpdater:
    Type: Custom::SecretUpdater
    Properties:
      ServiceToken: !GetAtt UpdateSecretLambdaFunction.Arn
      SecretArn: !Ref MyDBSecret  # ARN of the secret you want to update
      RDSEndpoint: !GetAtt MyDBInstance.Endpoint.Address  # Get the RDS instance endpoint
    DependsOn:
      - MyDBInstance
"""


def get_outputs() -> str:
    return """
  LambdaFunctionArn:
    Description: The ARN of the Lambda function
    Value: !GetAtt UpdateSecretLambdaFunction.Arn
"""
