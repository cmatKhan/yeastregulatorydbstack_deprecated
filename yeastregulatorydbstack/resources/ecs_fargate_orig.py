def get_parameters() -> str:
    return """
  LogGroup:
    Description: "The name of the CloudWatch Logs log group."
    Type: String
    Default: "djangoappstacklog"
    
  DjangoTaskDefinitionCPUs:
    Type: Number
    Description: The number of CPUs to use for the Django task definition
    Default: 256

  DjangoTaskDefinitionMemory:
    Type: Number
    Description: The amount of memory to use for the Django task definition
    Default: 512

  DjangoAppImage:
    Type: String
    Description: The Docker image for the Django app. eg 040367161929.dkr.ecr.us-east-2.amazonaws.com/django-stack:latest

  EnvFilePath:
    Type: String
    Description: The bucket/file to the environment file for the Django app. eg yeastregulatorydb-strides-tmp/django.env

  CeleryTaskDefinitionCPUs:
    Type: Number
    Description: The number of CPUs to use for the Celery task definition
    Default: 256

  CeleryTaskDefinitionMemory:
    Type: Number
    Description: The amount of memory to use for the Celery task definition
    Default: 512

  CeleryFlowerPort:
    Type: Number
    Description: The port for Celery Flower
    Default: 5555

  CeleryFlowerTaskDefinitionCPUs:
    Type: Number
    Description: The number of CPUs to use for the Celery Flower task definition
    Default: 256

  CeleryFlowerTaskDefinitionMemory:
    Type: Number
    Description: The amount of memory to use for the Celery Flower task definition
    Default: 512
"""


def get_resources() -> str:
    """
    Return the resources section of the ECS Fargate CloudFormation template.

    :return: resources section
    :rtype: str
    """
    return """
  ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Tags:
        - Key: app
          Value: !Ref AppTagValue
      Path: /
      Policies:
        - PolicyName: ECSExecutionPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ecs:StartTask
                  - ecs:StopTask
                  - ecs:DescribeTasks
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:CreateLogGroup
                  - ecr:GetAuthorizationToken
                  - ecr:BatchCheckLayerAvailability
                  - ecr:GetDownloadUrlForLayer
                  - ecr:BatchGetImage
                  - s3: GetObject
                Resource: '*'

  TaskRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Tags:
        - Key: app
          Value: !Ref AppTagValue
      Path: /
      Policies:
        - PolicyName: DjangoAppPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:*
                  - rds:*
                  - secretsmanager:GetSecretValue
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: '*'

  MyApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${LogGroup}"
      RetentionInDays: 14

  DjangoAppEcsCluster:
    Type: AWS::ECS::Cluster
    Properties:
      CapacityProviders:
        - FARGATE
      ClusterName: DjangoAppCluster
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  DjangoTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    DependsOn:
      - MyVPC
    Properties:
      VpcId: !Ref MyVPC
      Port: 5000
      Protocol: HTTP
      TargetType: ip
      HealthCheckProtocol: HTTP
      HealthCheckPath: /healthcheck
      Tags:
        - Key: app
          Value: !Ref AppTagValue


  DjangoTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    DependsOn:
      - ExecutionRole
      - TaskRole
      - MyElastiCacheRedis
      - MyDBInstance
      - MyApplicationLogGroup
    Properties:
      Family: django-app-family
      Cpu: !Ref DjangoTaskDefinitionCPUs
      Memory: !Ref DjangoTaskDefinitionMemory
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: django
          Image: !Ref DjangoAppImage
          Command:
            - /start
          Cpu: !Ref DjangoTaskDefinitionCPUs
          Memory: !Ref DjangoTaskDefinitionMemory
          Environment:
            - Name: AWS_DEFAULT_REGION
              Value: !Ref "AWS::Region"
            - Name: AWS_S3_REGION_NAME
              Value: !Ref "AWS::Region"
            - Name: REDIS_HOST
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Address
            - Name: REDIS_PORT
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Port
            - Name: POSTGRES_HOST
              Value: !GetAtt MyDBInstance.Endpoint.Address
            - Name: POSTGRES_PORT
              Value: !GetAtt MyDBInstance.Endpoint.Port
            - Name: POSTGRES_DB
              Value: !Ref DBName
            - Name: POSTGRES_USER
              Value: !Ref PostgresUser
            - Name: POSTGRES_PASSWORD
              Value: !Ref PostgresPassword
          EnvironmentFiles:
            - Value: !Sub "arn:aws:s3:::${EnvFilePath}"
              Type: s3
          PortMappings:
            - ContainerPort: 5000
              HostPort: 5000
              Protocol: tcp
          LogConfiguration:
            logDriver: awslogs
            options:
              awslogs-group: !Sub "/ecs/${LogGroup}"
              awslogs-region: !Ref "AWS::Region"
              awslogs-stream-prefix: ecs
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  DjangoService:
    Type: AWS::ECS::Service
    DependsOn:
      - DjangoAppEcsCluster
      - DjangoTaskDefinition
      - SubnetA
      - SubnetB
      - SubnetC
      - DjangoSecurityGroup
      - DjangoTargetGroup
    Properties:
      Cluster: !Ref DjangoAppEcsCluster
      TaskDefinition: !Ref DjangoTaskDefinition
      DesiredCount: 1
      EnableExecuteCommand: true
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          Subnets:
            - !Ref SubnetA
            - !Ref SubnetB
            - !Ref SubnetC
          SecurityGroups:
            - !GetAtt DjangoSecurityGroup.GroupId
      LoadBalancers:
        - TargetGroupArn: !Ref DjangoTargetGroup
          ContainerName: "django"
          ContainerPort: 80
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  CeleryWorkerTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    DependsOn:
      - ExecutionRole
      - TaskRole
      - MyElastiCacheRedis
      - MyDBInstance
      - MyApplicationLogGroup
    Properties:
      Family: your-celery-worker
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      RequiresCompatibilities:
        - FARGATE
      NetworkMode: awsvpc
      Cpu: !Ref CeleryTaskDefinitionCPUs
      Memory: !Ref CeleryTaskDefinitionMemory
      ContainerDefinitions:
        - Name: celery-worker
          Image: !Ref DjangoAppImage
          Command:
            - "/start-celeryworker"
          Environment:
            - Name: AWS_DEFAULT_REGION
              Value: !Ref "AWS::Region"
            - Name: AWS_S3_REGION_NAME
              Value: !Ref "AWS::Region"
            - Name: REDIS_HOST
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Address
            - Name: REDIS_PORT
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Port
            - Name: POSTGRES_HOST
              Value: !GetAtt MyDBInstance.Endpoint.Address
            - Name: POSTGRES_PORT
              Value: !GetAtt MyDBInstance.Endpoint.Port
            - Name: POSTGRES_DB
              Value: !Ref DBName
            - Name: POSTGRES_USER
              Value: !Ref PostgresUser
            - Name: POSTGRES_PASSWORD
              Value: !Ref PostgresPassword
          EnvironmentFiles:
            - Value: !Sub "arn:aws:s3:::${EnvFilePath}"
              Type: s3
          LogConfiguration:
            logDriver: awslogs
            options:
              awslogs-group: !Sub "/ecs/${LogGroup}"
              awslogs-region: !Ref "AWS::Region"
              awslogs-stream-prefix: ecs
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  CeleryWorkerService:
    Type: AWS::ECS::Service
    DependsOn:
      - SubnetA
      - SubnetB
      - SubnetC
      - DjangoSecurityGroup
      - CeleryWorkerTaskDefinition
    Properties:
      Cluster: !Ref DjangoAppEcsCluster
      TaskDefinition: !Ref CeleryWorkerTaskDefinition
      DesiredCount: 1
      LaunchType: FARGATE
      EnableExecuteCommand: true
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          Subnets:
            - !Ref SubnetA
            - !Ref SubnetB
            - !Ref SubnetC
          SecurityGroups:
            - !GetAtt DjangoSecurityGroup.GroupId
      # Removed LoadBalancers section
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  CeleryBeatTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    DependsOn:
      - ExecutionRole
      - TaskRole
      - MyElastiCacheRedis
      - MyDBInstance
      - MyApplicationLogGroup
    Properties:
      Family: your-celery-beat
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      RequiresCompatibilities:
        - FARGATE
      NetworkMode: awsvpc
      Cpu: !Ref CeleryTaskDefinitionCPUs
      Memory: !Ref CeleryTaskDefinitionMemory
      ContainerDefinitions:
        - Name: celery-beat
          Image: !Ref DjangoAppImage
          Command:
            - "/start-celerybeat"
          Environment:
            - Name: AWS_DEFAULT_REGION
              Value: !Ref "AWS::Region"
            - Name: AWS_S3_REGION_NAME
              Value: !Ref "AWS::Region"
            - Name: REDIS_HOST
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Address
            - Name: REDIS_PORT
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Port
            - Name: POSTGRES_HOST
              Value: !GetAtt MyDBInstance.Endpoint.Address
            - Name: POSTGRES_PORT
              Value: !GetAtt MyDBInstance.Endpoint.Port
            - Name: POSTGRES_DB
              Value: !Ref DBName
            - Name: POSTGRES_USER
              Value: !Ref PostgresUser
            - Name: POSTGRES_PASSWORD
              Value: !Ref PostgresPassword
          EnvironmentFiles:
            - Value: !Sub "arn:aws:s3:::${EnvFilePath}"
              Type: s3
          LogConfiguration:
            logDriver: awslogs
            options:
              awslogs-group: !Sub "/ecs/${LogGroup}"
              awslogs-region: !Ref "AWS::Region"
              awslogs-stream-prefix: ecs
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  CeleryBeatService:
    Type: AWS::ECS::Service
    DependsOn:
      - SubnetA
      - SubnetB
      - SubnetC
      - DjangoSecurityGroup
      - CeleryBeatTaskDefinition
    Properties:
      Cluster: !Ref DjangoAppEcsCluster
      TaskDefinition: !Ref CeleryBeatTaskDefinition
      DesiredCount: 1
      LaunchType: FARGATE
      EnableExecuteCommand: true
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          Subnets:
            - !Ref SubnetA
            - !Ref SubnetB
            - !Ref SubnetC
          SecurityGroups:
            - !GetAtt DjangoSecurityGroup.GroupId
      # Removed LoadBalancers section as it's unnecessary for Celery Beat
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  FlowerTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    DependsOn:
      - MyVPC
    Properties:
      VpcId: !Ref MyVPC
      Port: !Ref CeleryFlowerPort
      Protocol: HTTP
      TargetType: ip
      HealthCheckProtocol: HTTP
      HealthCheckPath: /health
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  FlowerTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    DependsOn:
      - ExecutionRole
      - TaskRole
      - MyElastiCacheRedis
      - MyDBInstance
      - MyApplicationLogGroup
    Properties:
      Family: your-flower
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      RequiresCompatibilities:
        - FARGATE
      NetworkMode: awsvpc
      Cpu: !Ref CeleryFlowerTaskDefinitionCPUs
      Memory: !Ref CeleryFlowerTaskDefinitionMemory
      ContainerDefinitions:
        - Name: flower
          Image: !Ref DjangoAppImage
          Command:
            - "/start-flower"
          Environment:
            - Name: AWS_DEFAULT_REGION
              Value: !Ref "AWS::Region"
            - Name: AWS_S3_REGION_NAME
              Value: !Ref "AWS::Region"
            - Name: REDIS_HOST
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Address
            - Name: REDIS_PORT
              Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Port
            - Name: POSTGRES_HOST
              Value: !GetAtt MyDBInstance.Endpoint.Address
            - Name: POSTGRES_PORT
              Value: !GetAtt MyDBInstance.Endpoint.Port
            - Name: POSTGRES_DB
              Value: !Ref DBName
            - Name: POSTGRES_USER
              Value: !Ref PostgresUser
            - Name: POSTGRES_PASSWORD
              Value: !Ref PostgresPassword
          EnvironmentFiles:
            - Value: !Sub "arn:aws:s3:::${EnvFilePath}"
              Type: s3
          PortMappings:
            - ContainerPort: 5555
              HostPort: 5555
              Protocol: tcp
          LogConfiguration:
            logDriver: awslogs
            options:
              awslogs-group: !Sub "/ecs/${LogGroup}"
              awslogs-region: !Ref "AWS::Region"
              awslogs-stream-prefix: ecs
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  FlowerService:
    Type: AWS::ECS::Service
    DependsOn:
      - SubnetA
      - SubnetB
      - SubnetC
      - DjangoSecurityGroup
      - FlowerTaskDefinition
      - FlowerTargetGroup
    Properties:
      Cluster: !Ref DjangoAppEcsCluster
      TaskDefinition: !Ref FlowerTaskDefinition
      DesiredCount: 1
      EnableExecuteCommand: true
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          Subnets:
            - !Ref SubnetA
            - !Ref SubnetB
            - !Ref SubnetC
          SecurityGroups:
            - !GetAtt DjangoSecurityGroup.GroupId
      LoadBalancers:
        - TargetGroupArn: !Ref FlowerTargetGroup
          ContainerName: "flower"
          ContainerPort: !Ref CeleryFlowerPort
      Tags:
        - Key: app
          Value: !Ref AppTagValue
"""


def get_outputs() -> str:
    """return the output string for this set of resources

    :return: output string
    :rtype: str
    """
    return """
  DjangoAppUrl:
    Description: URL for the Django app
    Value: !Sub "http://${DjangoStackLoadBalancer.DNSName}:80"
  FlowerUrl:
    Description: URL for Flower
    Value: !Sub "http://${DjangoStackLoadBalancer.DNSName}:5555"
  DjangoAppCluster:
    Description: Cluster for the Django app
    Value: !Ref DjangoAppEcsCluster
  DjangoAppTaskDefinition:
    Description: Task definition for the Django app
    Value: !Ref DjangoTaskDefinition
  CeleryWorkerTaskDefinition:
    Description: Task definition for the Celery worker
    Value: !Ref CeleryWorkerTaskDefinition
  CeleryBeatTaskDefinition:
    Description: Task definition for the Celery beat
    Value: !Ref CeleryBeatTaskDefinition
  FlowerTaskDefinition:
    Description: Task definition for Flower
    Value: !Ref FlowerTaskDefinition
    """
