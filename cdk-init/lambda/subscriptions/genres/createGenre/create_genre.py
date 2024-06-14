import json
import boto3
import uuid
from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Genres')

    body = json.loads(event['body'])

    item = {
        'genre': body.get('genre'),
    }

    table.put_item(Item=item)
    return create_response(201, {'message': 'Genre created successfully', 'genre': body.get('genre')})
