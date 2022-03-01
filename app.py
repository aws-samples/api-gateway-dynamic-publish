#!/usr/bin/env python3

import aws_cdk

from stacks.apigateway_dynamic_publish import ApiGatewayDynamicPublishStack

app = aws_cdk.App()
ApiGatewayDynamicPublishStack(app, "ApiGatewayDynamicPublish")

app.synth()
