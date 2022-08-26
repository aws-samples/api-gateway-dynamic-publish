#!/usr/bin/env python

"""
    greeting.py: 
    Simple Lambda Function handler that is the target for
    the API Gateway "Greeting" endpoint.
"""

import json
import logging
import traceback

# set logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    # read the event to json
    logger.debug(json.dumps(event, indent=2))

    try:
        
        # verify that the api_key query parameter is provided
        if 'queryStringParameters' not in event or 'greeting' not in event['queryStringParameters']:
            raise ValueError(f"greeting is expected as a query parameter but it was not present in the request; {event['rawPath']}")

        message = {"greeting": f"Hello {event['queryStringParameters']['greeting']}"}

        return {
            'statusCode': 200,
            'body': json.dumps(message, indent=2),
            'headers': {'Content-Type': 'application/json'}
        }
        
    except Exception as e:

        traceback.print_exception(type(e), value=e, tb=e.__traceback__)

        logger.error(f'Greeting error: {str(e)}')

        api_error = {"error": str(e)}

        return {
            'statusCode': 500,
            'body': json.dumps(api_error),
            'headers': {'Content-Type': 'application/json'}
        }
