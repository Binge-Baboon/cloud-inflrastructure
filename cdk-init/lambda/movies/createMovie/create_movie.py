import json
import boto3
import uuid
from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Movies')

    body = json.loads(event['body'])
    movie_id = str(uuid.uuid4())

    item = {
        'id': movie_id,
        'title': body.get('title'),
        'description': body.get('description'),
        'rating': body.get('rating'),
        'genres': body.get('genres'),
        'actors': body.get('actors'),
        'directors': body.get('directors'),
        'metadata': body.get('metadata')
    }

    table.put_item(Item=item)
    return create_response(201, {'message': 'Movie created successfully', 'id': movie_id})
