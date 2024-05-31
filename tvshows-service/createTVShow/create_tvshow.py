import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TVShows')

    data = json.loads(event['body'])
    tvshow_id = data['id']
    title = data['title']
    description = data['description']
    genres = data['genres']
    actors = data['actors']
    directors = data['directors']
    rating = data['rating']
    image_key = data['image_key']

    try:
        table.put_item(
            Item={
                'id': tvshow_id,
                'title': title,
                'description': description,
                'genres': genres,
                'actors': actors,
                'directors': directors,
                'rating': rating,
                'image_key': image_key
            }
        )
        return create_response(201, {'message': 'TVShow created successfully!'})
    except ClientError as e:
        return create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])