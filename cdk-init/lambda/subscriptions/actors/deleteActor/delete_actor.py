import json
import boto3
from shared.utils import create_response

def delete(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Actors')

    name = event['pathParameters']['name']

    response = table.delete_item(
        Key={
            'name': name.replace("-"," ")
        }
    )

    return create_response(200, {'message': 'Actor deleted successfully'})
