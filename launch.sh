#/usr/bin/env bash

aws cloudformation create-stack \
   --profile chasem \
  --stack-name "$1" \
  --template-body file:///home/oguzkhan/code/yeastregulatorydbstack/yeastregulatorydbstack/template_tester.txt \
  --parameters file:///home/oguzkhan/code/yeastregulatorydbstack/params.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --role-arn arn:aws:iam::040367161929:role/CloudFormationStackManager
