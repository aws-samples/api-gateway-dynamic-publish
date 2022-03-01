import aws_cdk as cdk
from aws_cdk.assertions import Template
from aws_cdk.assertions import Match

from stacks.apigateway_dynamic_publish import ApiGatewayDynamicPublishStack


def test_synthesizes_properly():
    app = cdk.App()

    # Create the ProcessorStack.
    apigateway_dynamic_publish_stack = ApiGatewayDynamicPublishStack(
        app,
        "ApiGatewayDynamicPublishStack"
    )

    # Prepare the stack for assertions.
    template = Template.from_stack(apigateway_dynamic_publish_stack)

    # Assert that we have the expected resources
    template.resource_count_is("AWS::S3::Bucket", 1)
    template.resource_count_is("AWS::KMS::Key", 1)
    template.resource_count_is("AWS::Lambda::Function", 5)
    template.resource_count_is("AWS::IAM::Role", 4)
    template.resource_count_is("AWS::IAM::Policy", 3)
    template.resource_count_is("AWS::Lambda::Permission", 2)
    template.resource_count_is("AWS::CloudFormation::CustomResource", 1)
    template.resource_count_is("Custom::S3AutoDeleteObjects", 1)
    template.resource_count_is("AWS::S3::BucketPolicy", 1)

    template.has_resource_properties(
        "AWS::IAM::Role",
        Match.object_equals(
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            }
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            "",
                            [
                                "arn:",
                                {
                                    "Ref": "AWS::Partition"
                                },
                                ":iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                            ]
                        ]
                    }
                ]
            }
        )
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        Match.object_equals(
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "apigateway:DELETE",
                                "apigateway:PUT",
                                "apigateway:PATCH",
                                "apigateway:POST",
                                "apigateway:GET"
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                "arn:aws:apigateway:*::/apis/*",
                                "arn:aws:apigateway:*::/apis"
                            ]
                        },
                        {
                            "Action": "logs:*",
                            "Effect": "Allow",
                            "Resource": "*"
                        },
                        {
                            "Action": [
                                "s3:GetObject*",
                                "s3:GetBucket*",
                                "s3:List*",
                                "s3:DeleteObject*",
                                "s3:PutObject",
                                "s3:PutObjectLegalHold",
                                "s3:PutObjectRetention",
                                "s3:PutObjectTagging",
                                "s3:PutObjectVersionTagging",
                                "s3:Abort*"
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                {
                                    "Fn::GetAtt": [
                                        Match.any_value(),
                                        "Arn"
                                    ]
                                },
                                {
                                    "Fn::Join": [
                                        "",
                                        [
                                            {
                                                "Fn::GetAtt": [
                                                    Match.any_value(),
                                                    "Arn"
                                                ]
                                            },
                                            "/*"
                                        ]
                                    ]
                                }
                            ]
                        },
                        {
                            "Action": [
                                "kms:Decrypt",
                                "kms:DescribeKey",
                                "kms:Encrypt",
                                "kms:ReEncrypt*",
                                "kms:GenerateDataKey*"
                            ],
                            "Effect": "Allow",
                            "Resource": {
                                "Fn::GetAtt": [
                                    Match.any_value(),
                                    "Arn"
                                ]
                            }
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "PolicyName": Match.any_value(),
                "Roles": [
                    {
                        "Ref": Match.any_value()
                    }
                ]
            }
        )
    )

    template.has_resource_properties(
        "AWS::Lambda::Permission",
        Match.object_equals(
            {
                "Action": "lambda:InvokeFunction",
                "FunctionName": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "Arn"
                    ]
                },
                "Principal": "apigateway.amazonaws.com",
                "SourceArn": {
                    "Fn::Join": [
                        "",
                        [
                            "arn:",
                            {
                                "Ref": "AWS::Partition"
                            },
                            ":execute-api:",
                            {
                                "Ref": "AWS::Region"
                            },
                            ":",
                            {
                                "Ref": "AWS::AccountId"
                            },
                            ":",
                            {
                                "Fn::GetAtt": [
                                    "ApiCreatorCustomResource",
                                    "ApiId"
                                ]
                            },
                            "/*/*/*"
                        ]
                    ]
                }
            }
        )
    )

    template.has_resource_properties(
        "AWS::CloudFormation::CustomResource",
        Match.object_equals(
            {
                "ServiceToken": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "Arn"
                    ]
                },
                "ApiGatewayAccessLogsLogGroupArn": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "Arn"
                    ]
                },
                "ApiIntegrationPingLambda": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "Arn"
                    ]
                },
                "ApiIntegrationGreetingLambda": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "Arn"
                    ]
                },
                "ApiDocumentationBucketName": {
                    "Ref": Match.any_value()
                },
                "ApiDocumentationBucketUrl": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "WebsiteURL"
                    ]
                },
                "ApiName": Match.any_value(),
                "ApiStageName": Match.any_value(),
                "ThrottlingBurstLimit": Match.any_value(),
                "ThrottlingRateLimit": Match.any_value()
            }
        )
    )

    template.has_resource_properties(
        "Custom::S3AutoDeleteObjects",
        Match.object_equals(
            {
                "ServiceToken": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "Arn"
                    ]
                },
                "BucketName": {
                    "Ref": Match.any_value()
                }
            }
        )
    )

    template.has_resource_properties(
        "AWS::S3::BucketPolicy",
        Match.object_equals(
            {
                "Bucket": {
                    "Ref": Match.any_value()
                },
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "s3:GetBucket*",
                                "s3:List*",
                                "s3:DeleteObject*"
                            ],
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": {
                                    "Fn::GetAtt": [
                                        Match.any_value(),
                                        "Arn"
                                    ]
                                }
                            },
                            "Resource": [
                                {
                                    "Fn::GetAtt": [
                                        Match.any_value(),
                                        "Arn"
                                    ]
                                },
                                {
                                    "Fn::Join": [
                                        "",
                                        [
                                            {
                                                "Fn::GetAtt": [
                                                    Match.any_value(),
                                                    "Arn"
                                                ]
                                            },
                                            "/*"
                                        ]
                                    ]
                                }
                            ]
                        }
                    ],
                    "Version": "2012-10-17"
                }
            }
        )
    )

    template.has_resource_properties(
        "Custom::S3AutoDeleteObjects",
        Match.object_equals(
            {
                "ServiceToken": {
                    "Fn::GetAtt": [
                        Match.any_value(),
                        "Arn"
                    ]
                },
                "BucketName": {
                    "Ref": Match.any_value()
                }
            }
        )
    )

    template.has_resource_properties(
        "AWS::S3::Bucket",
        Match.object_equals(
            {
                "BucketEncryption": {
                    "ServerSideEncryptionConfiguration": [
                        {
                            "ServerSideEncryptionByDefault": {
                                "KMSMasterKeyID": {
                                    "Fn::GetAtt": [
                                        Match.any_value(),
                                        "Arn"
                                    ]
                                },
                                "SSEAlgorithm": "aws:kms"
                            }
                        }
                    ]
                },
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True
                },
                "Tags": [
                    {
                        "Key": "aws-cdk:auto-delete-objects",
                        "Value": "true"
                    }
                ]
            }
        )
    )

    template.has_resource_properties(
        "AWS::KMS::Key",
        Match.object_equals(
            {
                "KeyPolicy": {
                    "Statement": [
                        {
                            "Action": "kms:*",
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": {
                                    "Fn::Join": [
                                        "",
                                        [
                                            "arn:",
                                            {
                                                "Ref": "AWS::Partition"
                                            },
                                            ":iam::",
                                            {
                                                "Ref": "AWS::AccountId"
                                            },
                                            ":root"
                                        ]
                                    ]
                                }
                            },
                            "Resource": "*"
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "Description": Match.any_value()
            }
        )
    )
