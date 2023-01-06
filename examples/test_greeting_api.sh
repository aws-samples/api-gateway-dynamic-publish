#!/bin/bash

###################################################################
# Script Name     : test_greeting_api.sh
# Description     : Test the API Gateway Greeting endpoint
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

# set the greeting you would like to send, ensure it is a single word with no spaces
GREETING="world"

STACK_NAME="ApiGatewayDynamicPublish"

# Get the API Endpoint
API_ENDPOINT_URL_EXPORT_NAME="api-gateway-dynamic-publish-url"
API_ENDPOINT_URL=$(aws cloudformation --region ${AWS_DEFAULT_REGION} describe-stacks --stack-name ${STACK_NAME} --query "Stacks[0].Outputs[?ExportName=='${API_ENDPOINT_URL_EXPORT_NAME}'].OutputValue" --output text)
API_GATEWAY_URL="${API_ENDPOINT_URL}"

################################################
# TEST Greetings API
################################################

echo "Testing GET ${API_GATEWAY_URL}/greeting?greeting=${GREETING}"
API_RESPONSE=$(curl -sX GET ${API_GATEWAY_URL}/greeting?greeting=${GREETING})

echo ""
echo ${API_RESPONSE}
echo ""