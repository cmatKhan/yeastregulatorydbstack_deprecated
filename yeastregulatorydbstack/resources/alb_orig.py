def get_parameters() -> str:
    return """
  HostedZoneId:
    Type: String
    Description: The ID of the Route 53 Hosted Zone. eg Z046780412JUUGA0O4T7

  SSLCertificateArn:
    Type: String
    Description: The ARN of the SSL certificate from AWS Certificate Manager. eg arn:aws:acm:us-east-2:040367161929:certificate/63b33893-d593-4ae0-8f34-c09b2ee96cad

  DNSName:
    Type: String
    Description: The DNS name for the record set. Eg, yeastregulatorydb.com

  FlowerHostHeader:
    Type: String
    Description: The host header value for the Flower listener rule. Eg, flower.yeastregulatorydb.com
"""


def get_resources():
    """
    Return the resources section of the Application Load Balancer
    """
    return """
  DjangoStackLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    DependsOn:
      - SubnetA
      - SubnetB
      - SubnetC
      - DjangoStackLoadBalancerSecurityGroup
    Properties:
      Name: DjangoStackLoadBalancer
      Scheme: internet-facing
      Subnets:
        - !Ref SubnetA
        - !Ref SubnetB
        - !Ref SubnetC
      SecurityGroups:
        - !Ref DjangoStackLoadBalancerSecurityGroup
      Type: application
      IpAddressType: ipv4
      Tags:
        - Key: app
          Value: !Ref AppTagValue

  HttpsListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    DependsOn:
      - DjangoStackLoadBalancer
    Properties:
      DefaultActions:
        - Type: redirect
          RedirectConfig:
            Protocol: HTTPS
            Port: 443
            StatusCode: HTTP_301
      LoadBalancerArn: !Ref DjangoStackLoadBalancer
      Port: 80
      Protocol: HTTP

  DjangoHttpsListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    DependsOn:
      - DjangoStackLoadBalancer
    Properties:
      Certificates:
        - CertificateArn: !Ref SSLCertificateArn
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref DjangoTargetGroup
      LoadBalancerArn: !Ref DjangoStackLoadBalancer
      Port: 443
      Protocol: HTTPS

  FlowerListenerRule:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    DependsOn:
      - DjangoHttpsListener
      - FlowerTargetGroup
    Properties:
      Actions:
        - Type: forward
          TargetGroupArn: !Ref FlowerTargetGroup
      Conditions:
        - Field: host-header
          Values:
            - !Ref FlowerHostHeader
      ListenerArn: !Ref DjangoHttpsListener
      Priority: 10
"""


def get_outputs() -> str:
    """
    Return the outputs section of the Application Load Balancer
    """
    return """
  LoadBalancerDNSName:
    Description: "DNS name of the Application Load Balancer"
    Value: !GetAtt DjangoStackLoadBalancer.DNSName

  
  """
