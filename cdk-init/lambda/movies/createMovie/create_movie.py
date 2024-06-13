import base64
import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response


def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')

    table = dynamodb.Table('Movies')
    bucket_name = 'binge-baboon-images'

    data = json.loads(event['body'])
    movie_id = data['id']
    title = data['title']
    genres = data['genres']
    actors = data['actors']
    directors = data['directors']
    image_data = data['image_data']

    image_key = f"{movie_id}.jpg"

    try:
        image_binary = base64.b64decode(image_data)

        s3.put_object(Bucket=bucket_name, Key=image_key, Body=image_binary, ContentType='image/jpeg')

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