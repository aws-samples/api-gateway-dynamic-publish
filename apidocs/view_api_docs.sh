#!/bin/bash

# set the desired AWS region below
AWS_REGION="eu-west-2"

# define the swagger ui version to download
SWAGGER_UI_RELEASE=4.5.2
SWAGGER_UI_RELEASE_URL=https://github.com/swagger-api/swagger-ui/archive/refs/tags/v${SWAGGER_UI_RELEASE}.zip

# define the root directory
ROOT_DIR=$PWD

echo "Preparing documentation ..."

# AWS Cloudformation stack name
STACK_NAME="ApiGatewayDynamicPublish"

echo "Grabbing Cloudformation exports for Stack Name: ${STACK_NAME}"

# the s3 bucket name containing the api documentation
DOC_BUCKET_EXPORT_NAME="api-gateway-dynamic-publish-documentation-name"
BUCKET_NAME=$(aws cloudformation --region ${AWS_REGION} describe-stacks --stack-name ${STACK_NAME} --query "Stacks[0].Outputs[?ExportName=='${DOC_BUCKET_EXPORT_NAME}'].OutputValue" --output text)

# ask the user for permission to download swagger ui
echo ""
echo "##################################"
echo ""
echo "To view API documentation in the OpenAPI format, it is necessary to download Swagger UI."
echo "Swagger UI is a third party, open source project licenced under the Apache License 2.0."
echo "See https://github.com/swagger-api/swagger-ui"
echo ""
echo "##################################"
echo ""

while true; do
    read -p "Would you like to download Swagger UI to view the API documentation? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y[yes] or n[no].";;
    esac
done

# create a tmp download directory
mkdir -p ${ROOT_DIR}/apidocs/.tmp

# create the swagger-ui directory
mkdir -p ${ROOT_DIR}/apidocs/swagger-ui

# grab the swagger ui release
wget --quiet -O ${ROOT_DIR}/apidocs/.tmp/v${SWAGGER_UI_RELEASE}.zip ${SWAGGER_UI_RELEASE_URL}
cd ${ROOT_DIR}/apidocs/.tmp

# unzip the swagger ui release and copy the dist folder
unzip -qq v${SWAGGER_UI_RELEASE}.zip
cp -r ${ROOT_DIR}/apidocs/.tmp/swagger-ui-${SWAGGER_UI_RELEASE}/dist/ ${ROOT_DIR}/apidocs/swagger-ui

# delete the tmp directory
rm -fr ${ROOT_DIR}/apidocs/.tmp

# grab the dynamic swagger.json file
cd ${ROOT_DIR}/apidocs/swagger-ui
aws s3 cp s3://${BUCKET_NAME}/swagger.json swagger.json --region ${AWS_REGION}

# replace the defeault json path with the swagger.json downloaded from s3
sed 's,https://petstore.swagger.io/v2/swagger.json,swagger.json,g' index.html | tee index.html > /dev/null 2>&1

cd ${ROOT_DIR}/apidocs

# install the npm dependencies
npm install express

# run a local nodejs server to visualize the dynamic documentation
node server.js

# return to starting directory
cd ${ROOT_DIR}