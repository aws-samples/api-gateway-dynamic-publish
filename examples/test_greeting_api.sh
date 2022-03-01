#!/bin/bash

# set the desired AWS region below
AWS_REGION="eu-central-1"

# set the greeting you would like to send, ensure it is a single word with no spaces
GREETING="world"

STACK_NAME="ApiGatewayDynamicPublish"

# Get the API Endpoint
API_ENDPOINT_URL_EXPORT_NAME="api-gateway-dynamic-publish-url"
API_ENDPOINT_URL=$(aws cloudformation --region ${AWS_REGION} describe-stacks --stack-name ${STACK_NAME} --query "Stacks[0].Outputs[?ExportName=='${API_ENDPOINT_URL_EXPORT_NAME}'].OutputValue" --output text)
API_GATEWAY_URL="${API_ENDPOINT_URL}"

################################################
# TEST Greetings API
################################################

echo "Testing GET ${API_GATEWAY_URL}/greeting?greeting=${GREETING}"
API_RESPONSE=$(curl -sX GET ${API_GATEWAY_URL}/greeting?greeting=${GREETING})

echo ""
echo ${API_RESPONSE}
echo ""