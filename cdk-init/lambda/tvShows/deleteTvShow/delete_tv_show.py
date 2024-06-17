import json
import boto3
from shared.utils import create_response

def delete(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TvShows')

    id = event['pathParameters']['id']

    response = table.delete_item(
        Key={
            'id': id
        }
    )

    return create_response(200, {'message': 'TvShow deleted successfully'})