import json
import boto3

from shared.utils import create_response

def get_all(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Episodes')

    response = table.scan()

    return create_response(200, response['Items'])