#!/bin/bash

# set the desired AWS region below
AWS_REGION="eu-central-1"

STACK_NAME="ApiGatewayDynamicPublish"

# Get the API Endpoint
API_ENDPOINT_URL_EXPORT_NAME="api-gateway-dynamic-publish-url"
API_ENDPOINT_URL=$(aws cloudformation --region ${AWS_REGION} describe-stacks --stack-name ${STACK_NAME} --query "Stacks[0].Outputs[?ExportName=='${API_ENDPOINT_URL_EXPORT_NAME}'].OutputValue" --output text)
API_GATEWAY_URL="${API_ENDPOINT_URL}"

################################################
# TEST Ping API
################################################

echo "Testing GET ${API_GATEWAY_URL}/ping"
API_RESPONSE=$(curl -sX GET ${API_GATEWAY_URL}/ping)

echo ""
echo ${API_RESPONSE}
echo ""