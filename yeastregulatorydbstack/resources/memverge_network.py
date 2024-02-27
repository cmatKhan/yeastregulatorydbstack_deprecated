"""
Construct the VPC and associated component CloudFormation parameters,
resources, and outputs. Note that this is hardcoded for region US-east-2
"""


def get_parameters() -> str:
    """
    Return the parameters section of the VPC, subnets, route tables,
    and network connections CloudFormation template.

    :return: parameters section
    :rtype: str
    """
    return """
  VpcCidrBlock:
    Type: String
    Default: 172.31.0.0/16
    Description: The CIDR block for the VPC.

  SubnetACidrBlock:
    Type: String
    Default: 172.31.0.0/20
    Description: The CIDR block for Subnet A.

  PrivateSubnetACidrBlock:
    Type: String
    Default: 172.31.48.0/20
    Description: The CIDR block for Private Subnet A.

  SubnetBCidrBlock:
    Type: String
    Default: 172.31.16.0/20
    Description: The CIDR block for Subnet B.

  PrivateSubnetBCidrBlock:
    Type: String
    Default: 172.31.64.0/20
    Description: The CIDR block for Private Subnet B.

  SubnetCCidrBlock:
    Type: String
    Default: 172.31.32.0/20
    Description: The CIDR block for Subnet C.

  PrivateSubnetCCidrBlock:
    Type: String
    Default: 172.31.80.0/20
    Description: The CIDR block for Private Subnet C

  AppTagValue:
    Type: String
    Default: yeastregulatorydb
    Description: The value for the `app` tag applied to all resources.
"""


def get_resources() -> str:
    """
    Return the resources section of the VPC, subnets, route tables,
    and network connections CloudFormation template.

    :return: resources section
    :rtype: str
    """
    return """
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidrBlock
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  SubnetA:
    Type: AWS::EC2::Subnet
    DependsOn:
      - MyVPC
      - PublicRoute
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref SubnetACidrBlock
      AvailabilityZone: us-east-2a
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  SubnetB:
    Type: AWS::EC2::Subnet
    DependsOn:
      - MyVPC
      - PublicRoute
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref SubnetBCidrBlock
      AvailabilityZone: us-east-2b
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  SubnetC:
    Type: AWS::EC2::Subnet
    DependsOn:
      - MyVPC
      - PublicRoute
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref SubnetCCidrBlock
      AvailabilityZone: us-east-2c
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  PrivateSubnetA:
    Type: AWS::EC2::Subnet
    DependsOn:
      - MyVPC
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref PrivateSubnetACidrBlock
      AvailabilityZone: us-east-2a
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  PrivateSubnetB:
    Type: AWS::EC2::Subnet
    DependsOn:
      - MyVPC
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref PrivateSubnetBCidrBlock
      AvailabilityZone: us-east-2b
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  PrivateSubnetC:
    Type: AWS::EC2::Subnet
    DependsOn:
      - MyVPC
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref PrivateSubnetCCidrBlock
      AvailabilityZone: us-east-2c
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  MyInternetGateway:
    Type: AWS::EC2::InternetGateway
    DependsOn:
      - MyVPC
    Properties:
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    DependsOn:
      - MyVPC
      - MyInternetGateway
    Properties:
      VpcId: !Ref MyVPC
      InternetGatewayId: !Ref MyInternetGateway

  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref MyVPC
      Tags:
        - Key: Name
          Value: PrivateRouteTable

  MyPublicRouteTable:
    Type: AWS::EC2::RouteTable
    DependsOn:
      - MyVPC
    Properties:
      VpcId: !Ref MyVPC
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn:
      - MyPublicRouteTable
      - AttachGateway
    Properties:
      RouteTableId: !Ref MyPublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref MyInternetGateway

  SubnetRouteTableAssociationA:
    Type: AWS::EC2::SubnetRouteTableAssociation
    DependsOn:
      - MyPublicRouteTable
      - SubnetA
    Properties:
      SubnetId: !Ref SubnetA
      RouteTableId: !Ref MyPublicRouteTable

  SubnetRouteTableAssociationB:
    Type: AWS::EC2::SubnetRouteTableAssociation
    DependsOn:
      - MyPublicRouteTable
      - SubnetB
    Properties:
      SubnetId: !Ref SubnetB
      RouteTableId: !Ref MyPublicRouteTable

  SubnetRouteTableAssociationC:
    Type: AWS::EC2::SubnetRouteTableAssociation
    DependsOn:
      - MyPublicRouteTable
      - SubnetC
    Properties:
      SubnetId: !Ref SubnetC
      RouteTableId: !Ref MyPublicRouteTable

  AssociationPrivateSubnetA:
    Type: AWS::EC2::SubnetRouteTableAssociation
    DependsOn:
      - PrivateRouteTable
      - PrivateSubnetA
    Properties:
      SubnetId: !Ref PrivateSubnetA
      RouteTableId: !Ref PrivateRouteTable

  AssociationPrivateSubnetB:
    Type: AWS::EC2::SubnetRouteTableAssociation
    DependsOn:
      - PrivateRouteTable
      - PrivateSubnetB
    Properties:
      SubnetId: !Ref PrivateSubnetB
      RouteTableId: !Ref PrivateRouteTable

  AssociationPrivateSubnetC:
    Type: AWS::EC2::SubnetRouteTableAssociation
    DependsOn:
      - PrivateRouteTable
      - PrivateSubnetC
    Properties:
      SubnetId: !Ref PrivateSubnetC
      RouteTableId: !Ref PrivateRouteTable
"""


def get_outputs() -> str:
    """
    Return the outputs section of the VPC, subnets, route tables,
    and network connections CloudFormation template.

    :return: outputs section
    :rtype: str
    """
    return """
  VPCId:
    Description: ID of the VPC
    Value: !Ref MyVPC

  SubnetAId:
    Description: ID of Subnet A
    Value: !Ref SubnetA

  SubnetBId:
    Description: ID of Subnet B
    Value: !Ref SubnetB

  SubnetCId:
    Description: ID of Subnet C
    Value: !Ref SubnetC

  PrivateSubnetAId:
    Description: ID of Private Subnet A
    Value: !Ref PrivateSubnetA

  PrivateSubnetBId:
    Description: ID of Private Subnet B
    Value: !Ref PrivateSubnetB

  PrivateSubnetCId:
    Description: ID of Private Subnet C
    Value: !Ref PrivateSubnetC

  InternetGatewayId:
    Description: ID of the Internet Gateway
    Value: !Ref MyInternetGateway

  PublicRouteTableId:
    Description: ID of the Public Route Table
    Value: !Ref MyPublicRouteTable
"""
