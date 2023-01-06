#!/bin/bash

###################################################################
# Script Name     : test_ping_api.sh
# Description     : Test the API Gateway Ping endpoint
#                   which was deployed as a CDK Stack.
# Args            :
# Author          : Damian McDonald
###################################################################

### <START> check if AWS credential variables are correctly set
if [ -z "${AWS_ACCESS_KEY_ID}" ]
then
      echo "AWS credential variable AWS_ACCESS_KEY_ID is empty."
      echo "Please see the guide below for instructions on how to configure your AWS CLI environment."
      echo "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html"
fi

if [ -z "${AWS_SECRET_ACCESS_KEY}" ]
then
      echo "AWS credential variable AWS_SECRET_ACCESS_KEY is empty."
      echo "Please see the guide below for instructions on how to configure your AWS CLI environment."
      echo "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html"
fi

if [ -z "${AWS_DEFAULT_REGION}" ]
then
      echo "AWS credential variable AWS_DEFAULT_REGION is empty."
      echo "Please see the guide below for instructions on how to configure your AWS CLI environment."
      echo "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html"
fi
### </END> check if AWS credential variables are correctly set

STACK_NAME="ApiGatewayDynamicPublish"

# Get the API Endpoint
API_ENDPOINT_URL_EXPORT_NAME="api-gateway-dynamic-publish-url"
API_ENDPOINT_URL=$(aws cloudformation --region ${AWS_DEFAULT_REGION} describe-stacks --stack-name ${STACK_NAME} --query "Stacks[0].Outputs[?ExportName=='${API_ENDPOINT_URL_EXPORT_NAME}'].OutputValue" --output text)
API_GATEWAY_URL="${API_ENDPOINT_URL}"

################################################
# TEST Ping API
################################################

echo "Testing GET ${API_GATEWAY_URL}/ping"
API_RESPONSE=$(curl -sX GET ${API_GATEWAY_URL}/ping)

echo ""
echo ${API_RESPONSE}
echo ""