import json
import boto3
from shared.utils import create_response

def delete(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    email = event['pathParameters']['email']

    response = table.delete_item(
        Key={
            'email': email
        }
    )

    return create_response(200, {'message': 'User with email ' + email + ' deleted successfully'})
