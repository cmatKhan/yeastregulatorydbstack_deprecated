"""AWS CloudFormation template for RDS, ElastiCache, and EC2 resources.

NOTE: This requires a vpc_subnets_routetables_networkcon.py file with subnets
named SubnetA, SubnetB, and SubnetC.

NOTE: This requires a vpc_subnets_routetables_networkcon.py file with a vpc
named MyVPC.
"""


def get_parameters() -> str:
    """Return the parameters section of the RDS/ElstiCache/EC2 CloudFormation
    template."""
    return """

  DBName:
    Type: String
    Description: The name of the database. Eg, yeastregulatorydb

  PostgresUser:
    Type: String
    Description: The master username for the RDS instance
    Default: postgres

  PostgresPassword:
    Type: String
    Description: The master password for the RDS instance. Must be at least 8 characters long.
    NoEcho: true

  PostgresVersion:
    Type: String
    Description: The version of Postgres to use for the RDS instance
    Default: 15.2
  
  PostgresVersionFamily:
    Type: String
    Description: The version family of Postgres to use for the RDS instance
    Default: postgres15

  RdsInstanceType:
    Type: String
    Description: The instance type for the RDS instance
    Default: db.t3.micro

  RdsAllocatedStorage:
    Type: String
    Description: The allocated storage for the RDS instance
    Default: 20

  ElasticacheInstanceType:
    Type: String
    Description: The instance type for the ElastiCache Redis instance
    Default: cache.t2.micro
"""


def get_resources() -> str:
    """return a string of resources for the rds, redis, and ec2 instances."""
    resources_list = [
        """
  MyCustomParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Custom parameter group for my DB
      Family: !Ref PostgresVersionFamily
      Parameters:
        max_connections: "200"
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  MyDBProxyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: rds.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: RDSProxyPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                  - secretsmanager:DescribeSecret
                Resource: '*'
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  MyDBSecret:
    Type: AWS::SecretsManager::Secret
    DependsOn: MyDBInstance
    Properties:
      Name: MyDBSecret
      Description: RDS database credentials
      SecretString: !Sub '{"username": "${PostgresUser}", "password": "${PostgresPassword}"}'
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  MyDBProxy:
    Type: AWS::RDS::DBProxy
    DependsOn:
      - MyDBProxyRole
      - MyDBSecret
    Properties:
      DBProxyName: mydbproxy
      EngineFamily: POSTGRESQL
      Auth:
        - AuthScheme: SECRETS
          IAMAuth: DISABLED
          SecretArn: !Ref MyDBSecret
      RoleArn: !GetAtt MyDBProxyRole.Arn
      VpcSecurityGroupIds:
        - !Ref MyDBSecurityGroup
      VpcSubnetIds:
        - !Ref SubnetA
        - !Ref SubnetB
        - !Ref SubnetC
      RequireTLS: false
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  MyDBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: "My DB Subnet Group"
      SubnetIds:
        - !Ref PrivateSubnetA
        - !Ref PrivateSubnetB
        - !Ref PrivateSubnetC

  MyDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBName: !Ref DBName
      AllocatedStorage: !Ref RdsAllocatedStorage
      DBInstanceClass: !Ref RdsInstanceType
      Engine: postgres
      EngineVersion: !Ref PostgresVersion
      MasterUsername: !Ref PostgresUser
      MasterUserPassword: !Ref PostgresPassword
      BackupRetentionPeriod: 3
      DBSubnetGroupName: !Ref MyDBSubnetGroup
      VPCSecurityGroups:
        - !Ref MyDBSecurityGroup
      DBParameterGroupName: !Ref MyCustomParameterGroup
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  MyElastiCacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: "Subnet group for ElastiCache"
      SubnetIds:
        - !Ref PrivateSubnetA
        - !Ref PrivateSubnetB
        - !Ref PrivateSubnetC
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  MyElastiCacheRedis:
    Type: AWS::ElastiCache::CacheCluster
    DependsOn:
      - MyCacheSecurityGroup
      - RedisSecurityGroup
      - MyElastiCacheSubnetGroup
    Properties:
      CacheNodeType: !Ref ElasticacheInstanceType
      Engine: redis
      NumCacheNodes: 1
      VpcSecurityGroupIds:
        - !Ref MyCacheSecurityGroup
        - !Ref RedisSecurityGroup
      CacheSubnetGroupName: !Ref MyElastiCacheSubnetGroup
      Tags:
        - Key: app
          Value: !Ref AppTagValue
    """,
    ]

    return "\n".join(resources_list)


def get_outputs():
    """
    Return the outputs section of the RDS/ElstiCache/EC2
    CloudFormation template.
    """
    return """
  RDSInstanceEndpoint:
    Description: Endpoint of the RDS instance
    Value: !GetAtt MyDBInstance.Endpoint.Address

  RDSProxyEndpoint:
    Description: Endpoint of the RDS Proxy
    Value: !GetAtt MyDBProxy.Endpoint

  RedisEndpoint:
    Description: Endpoint of the Redis ElastiCache instance
    Value: !GetAtt MyElastiCacheRedis.RedisEndpoint.Address
"""
