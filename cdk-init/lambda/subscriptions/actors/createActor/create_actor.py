import json
import boto3
import uuid
from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Actors')

    body = json.loads(event['body'])

    item = {
        'name': body.get('name'),
    }

    table.put_item(Item=item)
    return create_response(201, {'message': 'Actor created successfully', 'name': body.get('name')})
