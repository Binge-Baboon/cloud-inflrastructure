import json
import boto3
import uuid
from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    body = json.loads(event['body'])


    item = {
        'username': body.get('username'),
        'email': body.get('email'),
        'firstName': body.get('firstName'),
        'lastName': body.get('lastName'),
        'phone': body.get('phone'),
        'address': body.get('address'),
        'subscribed': body.get('subscribed'),
        'watched': body.get('watched'),
        'downloads': body.get('downloads')
    }

    table.put_item(Item=item)
    return create_response(201, {'message': 'User created successfully', 'username': body.get('username')})
