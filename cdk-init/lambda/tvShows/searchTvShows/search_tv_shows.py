import json
import boto3
from shared.utils import create_response

def search(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TvShows')

    body = json.loads(event['body'])

    response = table.scan()
    items = response.get('Items', [])

    title = body.get('title')
    description = body.get('description')
    actors = body.get('actors', [])
    directors = body.get('directors', [])
    genres = body.get('genres', [])



    filtered_items = [
        item for item in items
        if (not title or title.lower() in item.get('title', '').lower())
        and (not description or description.lower() in item.get('description', '').lower())
        and (not actors or any(actor in item.get('actors', []) for actor in actors))
        and (not directors or any(director in item.get('directors', []) for director in directors))
        and (not genres or any(genre in item.get('genres', []) for genre in genres))
    ]

    return create_response(200, filtered_items)

