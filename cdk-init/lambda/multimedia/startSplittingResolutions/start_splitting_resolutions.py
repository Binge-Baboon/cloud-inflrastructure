import json
import os
import boto3

from shared.utils import create_response

client = boto3.client('stepfunctions')


def handler(event, context):
    state_machine_arn = os.environ['STATE_MACHINE_ARN']
    body = json.loads(event['body'])
    key = body['key']
    input_payload = json.dumps({"key": key})

    response = client.start_execution(
        stateMachineArn=state_machine_arn,
        input=input_payload
    )

    return create_response(200, {'response': response})

