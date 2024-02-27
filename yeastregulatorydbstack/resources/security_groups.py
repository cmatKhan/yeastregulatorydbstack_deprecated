def get_parameters() -> str:
    """Return the parameters section of the security groups CloudFormation"""
    return """"""


def get_resources() -> str:
    """define the stack security groups

    :return: a yaml formatted str suitable for adding to the Resources section of a CloudFormation template
    :rtype: str
    """
    return """
  DjangoSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    DependsOn:
      - MyVPC
    Properties:
      GroupDescription: Security group for Django ECS service allowing HTTP and HTTPS traffic
      VpcId: !Ref MyVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  RedisSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    DependsOn:
      - MyVPC
      - DjangoSecurityGroup
    Properties:
      GroupDescription: Security group for Redis service
      VpcId: !Ref MyVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref DjangoSecurityGroup
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  PostgresSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    DependsOn:
      - MyVPC
      - DjangoSecurityGroup
    Properties:
      GroupDescription: Security group for Postgres database
      VpcId: !Ref MyVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref DjangoSecurityGroup
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  DjangoStackLoadBalancerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    DependsOn:
      - MyVPC
    Properties:
      GroupDescription: "Security group for ALB allowing HTTP and HTTPS traffic"
      VpcId: !Ref MyVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: app
          Value: !Ref AppTagValue
  
  DjangoEC2SecurityGroup:
      Type: AWS::EC2::SecurityGroup
      DependsOn:
          - MyVPC
      Properties:
        GroupDescription: Security group for EC2 instance
        VpcId: !Ref MyVPC
        SecurityGroupIngress:
            - IpProtocol: tcp
              FromPort: 22
              ToPort: 22
              CidrIp: 107.200.64.20/32
            - IpProtocol: tcp
              FromPort: 80
              ToPort: 80
              CidrIp: 0.0.0.0/0
        Tags:
          - Key: app
            Value: !Ref AppTagValue

  MyDBSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      DependsOn:
          - MyVPC
          - DjangoEC2SecurityGroup
          - DjangoSecurityGroup
      Properties:
        GroupDescription: Allow access to PostgreSQL
        VpcId: !Ref MyVPC
        SecurityGroupIngress:
            - IpProtocol: tcp
              FromPort: 5432
              ToPort: 5432
              SourceSecurityGroupId: !Ref DjangoEC2SecurityGroup
            - IpProtocol: tcp
              FromPort: 5432
              ToPort: 5432
              SourceSecurityGroupId: !Ref DjangoSecurityGroup
        Tags:
          - Key: app
            Value: !Ref AppTagValue

  MyCacheSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      DependsOn:
          - MyVPC
          - DjangoEC2SecurityGroup
      Properties:
        GroupDescription: Allow access to Redis
        VpcId: !Ref MyVPC
        SecurityGroupIngress:
            - IpProtocol: tcp
              FromPort: 6379
              ToPort: 6379
              SourceSecurityGroupId: !Ref DjangoEC2SecurityGroup
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
  DjangoSecurityGroup:
    Description: Security group for the Django app
    Value: !GetAtt DjangoSecurityGroup.GroupId

  RedisSecurityGroup:
    Description: Security group for Redis
    Value: !GetAtt RedisSecurityGroup.GroupId

  PostgresSecurityGroup:
    Description: Security group for Postgres
    Value: !GetAtt PostgresSecurityGroup.GroupId

  DjangoStackLoadBalancerSecurityGroup:
    Description: Security group for ALB
    Value: !GetAtt DjangoStackLoadBalancerSecurityGroup.GroupId

  MyDBSecurityGroup:
    Description: Security group for PostgreSQL
    Value: !GetAtt MyDBSecurityGroup.GroupId

  MyCacheSecurityGroup:
    Description: Security group for Redis
    Value: !GetAtt MyCacheSecurityGroup.GroupId

  DjangoEC2SecurityGroup:
    Description: Security group for EC2 instance
    Value: !GetAtt DjangoEC2SecurityGroup.GroupId
    """
