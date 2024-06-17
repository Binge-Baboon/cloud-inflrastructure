import json
import boto3
from shared.utils import create_response
def get_one(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TvShows')

    id = event['pathParameters']['id']
    response = table.get_item(
        Key={
            'id': id
        }
    )

    if 'Item' in response:
        item = response['Item']
        return create_response(200, item)
    else:
        return create_response(404, {'message': 'TvShow not found'})
