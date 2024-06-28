import json
import boto3
import uuid
from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TvShows')

    body = json.loads(event['body'])
    id = str(uuid.uuid4())

    item = {
        'id': id,
        'title': body.get('title'),
        'description': body.get('description'),
        'rating': body.get('rating', {}),
        'genres': body.get('genres'),
        'actors': body.get('actors'),
        'directors': body.get('directors'),
        'episodes': body.get('episodes', {})
    }

    table.put_item(Item=item)
    return create_response(201, {'message': 'TvShow created successfully', 'tvShow': item})
