import json
import boto3
import uuid
from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Directors')

    body = json.loads(event['body'])

    item = {
        'name': body.get('name'),
    }

    table.put_item(Item=item)
    return create_response(201, {'message': 'Director created successfully', 'name': body.get('name')})
