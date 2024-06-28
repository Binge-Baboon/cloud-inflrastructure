import json
import boto3
from shared.utils import create_response

def get_one(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Genres')

    genre = event['pathParameters'][('genre')]
    response = table.get_item(
        Key={
            'genre': genre
        }
    )

    if 'Item' in response:
        item = response['Item']
        return create_response(200, item)
    else:
        return create_response(404, {'message': 'Genre not found'})
