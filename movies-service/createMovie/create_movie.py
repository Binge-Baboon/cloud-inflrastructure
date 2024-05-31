import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Movies')

    data = json.loads(event['body'])
    movie_id = data['id']
    title = data['title']
    genres = data['genres']
    actors = data['actors']
    directors = data['directors']
    image_key = data['image_key']

    try:
        table.put_item(
            Item={
                'id': movie_id,
                'title': title,
                'genres': genres,
                'actors': actors,
                'directors': directors,
                'image_key': image_key
            }
        )
        return create_response(201, {'message': 'Movie created successfully!'})
    except ClientError as e:
        return create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])