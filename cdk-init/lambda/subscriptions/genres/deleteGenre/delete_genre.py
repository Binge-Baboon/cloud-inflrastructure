import json
import boto3
from shared.utils import create_response

def delete(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Genres')

    genre = event['pathParameters']['genre']

    response = table.delete_item(
        Key={
            'genre': genre
        }
    )

    return create_response(200, {'message': 'Genre deleted successfully'})
