from aws_cdk import (
    Stack,
    RemovalPolicy,
    BundlingOptions,
    CfnOutput,
    CustomResource,
    Duration,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda,
    aws_logs as logs,
    custom_resources
)
from constructs import Construct
import os
import json


class ApiGatewayDynamicPublishStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = self.read_cdk_context_json()

        ##########################################################
        # <START> API Gateway Documentation Bucket
        ##########################################################

        api_documentation_bucket = s3.Bucket(
            self,
            'ApiDocumentationBucket',
            encryption=s3.BucketEncryption.KMS,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=False
        )

        ##########################################################
        # </END> API Gateway Documentation Bucket
        ##########################################################


        ##########################################################
        # <START> API Gateway Access Logs Group
        ##########################################################

        # create log group for API Gateway access logs
        api_gateway_access_log_group = logs.LogGroup(
            self, 
            'ApiGatewayAccessLogGroup',
            log_group_name='/aws/vendedlogs/ApiGatewayAccessLogs',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.TWO_WEEKS
        )


        ##########################################################
        # <START> API Gateway Lambda Integrations
        ##########################################################

        # IAM Role for Lambda
        api_gateway_integration_lambda_role = iam.Role(
            scope=self,
            id="ApiGatewayIntegrationLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )
  
        api_gateway_integration_lambda_role.add_to_policy(
            iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:ListLogDeliveries"
                    ]
                )
        )

        api_gateway_ping_lambda = aws_lambda.Function(
            scope=self,
            id="ApiGatewayPingLambda",
            code=aws_lambda.Code.from_asset(f"{os.path.dirname(__file__)}/resources/api_integrations"),
            handler="ping.lambda_handler",
            role=api_gateway_integration_lambda_role,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(15)
        )

        api_gateway_greeting_lambda = aws_lambda.Function(
            scope=self,
            id="ApiGatewayGreetingLambda",
            code=aws_lambda.Code.from_asset(f"{os.path.dirname(__file__)}/resources/api_integrations"),
            handler="greeting.lambda_handler",
            role=api_gateway_integration_lambda_role,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(15)
        )

        ##########################################################
        # </END> Create API Creator Custom Resource
        ##########################################################


        ##########################################################
        # <START> Create API Creator Custom Resource
        ##########################################################

        # Create a role for the api creator lambda function
        apicreator_lambda_role = iam.Role(
            scope=self,
            id="ApiCreatorLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )

        apicreator_lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    "arn:aws:apigateway:*::/apis/*",
                    "arn:aws:apigateway:*::/apis"
                ],
                actions=[
                    "apigateway:DELETE",
                    "apigateway:PUT",
                    "apigateway:PATCH",
                    "apigateway:POST",
                    "apigateway:GET"
                ]
            )
        )

        apicreator_lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=[
                    "logs:*"
                ]
            )
        )

        api_documentation_bucket.grant_read_write(apicreator_lambda_role)

        apicreator_lambda = aws_lambda.Function(
            scope=self,
            id="ApiCreatorLambda",
            code=aws_lambda.Code.from_asset( 
                f"{os.path.dirname(__file__)}/resources/api_creation",
                bundling=BundlingOptions(
                    image=aws_lambda.Runtime.PYTHON_3_9.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output"
                    ],
                ),
            ),
            handler="api_creator.lambda_handler",
            role=apicreator_lambda_role,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.minutes(5)
        )

        # Provider that invokes the api creator lambda function
        apicreator_provider = custom_resources.Provider(
            self,
            'ApiCreatorCustomResourceProvider',
            on_event_handler=apicreator_lambda
        )

        # The custom resource that uses the api creator provider to supply values
        apicreator_custom_resource = CustomResource(
            self,
            'ApiCreatorCustomResource',
            service_token=apicreator_provider.service_token,
            properties={
                'ApiGatewayAccessLogsLogGroupArn': api_gateway_access_log_group.log_group_arn,
                'ApiIntegrationPingLambda': api_gateway_ping_lambda.function_arn,
                'ApiIntegrationGreetingLambda': api_gateway_greeting_lambda.function_arn,
                'ApiDocumentationBucketName': api_documentation_bucket.bucket_name,
                'ApiDocumentationBucketUrl': api_documentation_bucket.bucket_website_url,
                'ApiName': f"{config['api']['apiName']}",
                'ApiStageName': config['api']['apiStageName'],
                'ThrottlingBurstLimit': config['api']['throttlingBurstLimit'],
                'ThrottlingRateLimit': config['api']['throttlingRateLimit']
            }
        )

        ##########################################################
        # </END> Create API Creator Custom Resource
        ##########################################################

        ##########################################################
        # <START> Create AWS API Gateway permissions
        ##########################################################

        apigateway_id = CustomResource.get_att_string(apicreator_custom_resource, attribute_name='ApiId')
        apigateway_endpoint = CustomResource.get_att_string(apicreator_custom_resource, attribute_name='ApiEndpoint')
        apigateway_stagename = CustomResource.get_att_string(apicreator_custom_resource, attribute_name='ApiStageName')

        http_api_arn = (
            f"arn:{self.partition}:execute-api:"
            f"{self.region}:{self.account}:"
            f"{apigateway_id}/*/*/*"
        )

        # grant HttpApi permission to invoke api lambda function
        api_gateway_ping_lambda.add_permission(
            f"Invoke By Orchestrator Gateway Permission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=http_api_arn
        )

        api_gateway_greeting_lambda.add_permission(
            f"Invoke By Orchestrator Gateway Permission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=http_api_arn
        )

        ##########################################################
        # </END> Create AWS API Gateway permissions
        ##########################################################


        ##########################################################
        # <START> Stack exports
        ##########################################################

        CfnOutput(
            self, 
            id=f"api-gateway-dynamic-publish-id", 
            value=apigateway_id, 
            export_name="api-gateway-dynamic-publish-id"
        
        )

        CfnOutput(
            self, 
            id="api-gateway-dynamic-publish-endpoint", 
            value=apigateway_endpoint, 
            export_name="api-gateway-dynamic-publish-endpoint"
            )
        
        CfnOutput(
            self, 
            id="api-gateway-dynamic-publish-stagename", 
            value=apigateway_stagename, 
            export_name="api-gateway-dynamic-publish-stagename"
        )

        CfnOutput(
            self, 
            id="api-gateway-dynamic-publish-url", 
            value=f"{apigateway_endpoint}/{apigateway_stagename}", 
            export_name="api-gateway-dynamic-publish-url"
        )

        CfnOutput(
            self, 
            id="api-gateway-dynamic-publish-arn", 
            value=http_api_arn, 
            export_name="api-gateway-dynamic-publish-arn"
        )
    
        CfnOutput(
            self, 
            id="api-gateway-dynamic-publish-documentation-name", 
            value=api_documentation_bucket.bucket_name, 
            export_name="api-gateway-dynamic-publish-documentation-name"
        )

        ##########################################################
        # </END> Stack exports
        ##########################################################


    def read_cdk_context_json(self):
        filename = "cdk.json"

        with open(filename, 'r') as my_file:
            data = my_file.read()

        obj = json.loads(data)

        return obj.get('context')