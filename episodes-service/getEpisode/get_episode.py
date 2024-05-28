import json
import boto3

from shared.utils import create_response

def get_one(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Episodes')

    episode_id = event['pathParameters']['id']
    response = table.get_item(
        Key={
            'id': int(episode_id)
        }
    )
    if 'Item' in response:
        return create_response(200, response['Item'])
    else:
        return create_response(404, {'message': 'Episode not found'})
