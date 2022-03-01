import boto3
import json
import logging
import os
import yaml

# set logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# environment variables
aws_region = os.environ['AWS_REGION']

# boto3 clients
apigateway_client = boto3.client('apigatewayv2')
s3_client = boto3.client('s3')

def replace_placeholders(template_file: str, substitutions: dict) -> str:
    import re

    def from_dict(dct):
        def lookup(match):
            key = match.group(1)
            return dct.get(key, f'<{key} not found>')
        return lookup

    with open (template_file, "r") as template_file:
        template_data = template_file.read()

    # perform the subsitutions, looking for placeholders @@PLACEHOLDER@@
    api_template = re.sub('@@(.*?)@@', from_dict(substitutions), template_data)

    return api_template


def get_api_by_name(api_name: str) -> str:
    get_apis = apigateway_client.get_apis()
    for api in get_apis['Items']:
        if api['Name'] == api_name:
            return api['ApiId']

    return None


def create_api(api_template:str):
    api_response = apigateway_client.import_api(
        Body=api_template,
        FailOnWarnings=True
    )

    return api_response['ApiEndpoint'], api_response['ApiId']


def update_api(api_template: str, api_name:str):
    
    api_id = get_api_by_name(api_name)

    if api_id is not None:
        api_response = apigateway_client.reimport_api(
            ApiId=api_id,
            Body=api_template,
            FailOnWarnings=True
        )
        return api_response['ApiEndpoint'], api_response['ApiId']


def delete_api(api_name: str):
    if get_api_by_name(api_name) is not None:
        response = apigateway_client.delete_api(
            ApiId=get_api_by_name(api_name)
        )


def deploy_api(
        api_id: str, 
        api_stage_name: str,
        api_access_logs_arn: str,
        throttling_burst_limit: int, 
        throttling_rate_limit: int
    ):
    apigateway_client.create_stage(
        AccessLogSettings={
            'DestinationArn': api_access_logs_arn,
            'Format': '$context.identity.sourceIp - - [$context.requestTime] "$context.httpMethod $context.routeKey $context.protocol" $context.status $context.responseLength $context.requestId $context.integrationErrorMessage'
        },
        ApiId=api_id,
        StageName=api_stage_name,
        AutoDeploy=True,
        DefaultRouteSettings={
            'DetailedMetricsEnabled': True,
            'ThrottlingBurstLimit':throttling_burst_limit,
            'ThrottlingRateLimit': throttling_rate_limit
        }
    )


def delete_api_deployment(api_id: str, api_stage_name: str):
    try:
        apigateway_client.get_stage(
            ApiId=api_id,
            StageName=api_stage_name
        )

        apigateway_client.delete_stage(
            ApiId=api_id,
            StageName=api_stage_name
        )
    except apigateway_client.exceptions.NotFoundException as e:
        logger.error(f"Stage name: {api_stage_name} for api id: {api_id} was not found during stage deletion. This is an expected error condition and is handled in code.")
    except Exception as e:
        raise ValueError(f"Unexpected error encountered during api deployment deletion: {str(e)}")


def publish_api_documentation(bucket_name, api_definition):

    api_definition_json=json.dumps(yaml.safe_load(api_definition))    

    with open("/tmp/swagger.json", "w") as swagger_file:
        swagger_file.write(api_definition_json)

    # Upload the file
    try:

        s3_client.upload_file("/tmp/swagger.json", bucket_name, "swagger.json")

    except Exception as e:
        logging.error(str(e))
        raise ValueError(str(e))


def lambda_handler(event, context):
    
    # print the event details
    logger.debug(json.dumps(event, indent=2))

    props = event['ResourceProperties']
    api_gateway_access_log_group_arn = props['ApiGatewayAccessLogsLogGroupArn']
    api_integration_ping_lambda = props['ApiIntegrationPingLambda']
    api_integration_greetings_lambda = props['ApiIntegrationGreetingLambda']
    api_name = props['ApiName']
    api_stage_name = props['ApiStageName']
    api_documentation_bucket_name = props['ApiDocumentationBucketName']
    throttling_burst_limit = int(props['ThrottlingBurstLimit'])
    throttling_rate_limit = int(props['ThrottlingRateLimit'])

    lambda_substitutions = {
        "API_NAME": api_name,
        "API_INTEGRATION_PING_LAMBDA": f"arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/{api_integration_ping_lambda}/invocations",
        "API_INTEGRATION_GREETING_LAMBDA": f"arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/{api_integration_greetings_lambda}/invocations"
    }

    api_template = replace_placeholders("api_definition.yaml", lambda_substitutions)

    if event['RequestType'] != 'Delete':

        if get_api_by_name(api_name) is None:

            logger.debug("Creating API")

            api_endpoint, api_id = create_api(api_template)

            deploy_api(api_id, api_stage_name, api_gateway_access_log_group_arn, throttling_burst_limit, throttling_rate_limit)

            publish_api_documentation(api_documentation_bucket_name, api_template)

            output = {
                'PhysicalResourceId': f"generated-api",
                'Data': {
                    'ApiEndpoint': api_endpoint,
                    'ApiId': api_id,
                    'ApiStageName': api_stage_name
                }
            }
            
            return output

        else:

            logger.debug("Updating API")

            api_endpoint, api_id = update_api(api_template, api_name)

            # delete and redeploy the stage after updating the api definition
            delete_api_deployment(api_id, api_stage_name)
            deploy_api(api_id, api_stage_name, api_gateway_access_log_group_arn, throttling_burst_limit, throttling_rate_limit)

            publish_api_documentation(api_documentation_bucket_name, api_template)

            output = {
                'PhysicalResourceId': f"generated-api",
                'Data': {
                    'ApiEndpoint': api_endpoint,
                    'ApiId': api_id,
                    'ApiStageName': api_stage_name
                }
            }
        
        return output

    if event['RequestType'] == 'Delete':

        logger.debug("Deleting API")

        if get_api_by_name(api_name) is not None:
            delete_api(api_name)

        output = {
            'PhysicalResourceId': f"generated-api",
            'Data': {
                'ApiEndpoint': "Deleted",
                'ApiId': "Deleted",
                'ApiStageName': "Deleted"
            }
        }
        logger.info(output)
        
        return output
