import json
import boto3
from shared.utils import create_response

def get_all(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Genres')

    response = table.scan()
    items = response.get('Items', [])
    return create_response(200, items)