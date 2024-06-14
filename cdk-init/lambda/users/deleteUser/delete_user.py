import json
import boto3
from shared.utils import create_response

def delete(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    username = event['pathParameters']['username']

    response = table.delete_item(
        Key={
            'username': username
        }
    )

    return create_response(200, {'message': 'User with username ' + username + ' deleted successfully'})
