import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Episodes')

    data = json.loads(event['body'])
    episode_id = data['id']
    title = data['title']
    description = data['description']
    season = data['season']
    episode = data['episode']
    tvshow_id = data['tvshow_id']
    video_id = data['video_id']
    image_key = data['image_key']

    try:
        table.put_item(
            Item={
                'id': episode_id,
                'title': title,
                'description': description,
                'season': season,
                'episode': episode,
                'tvshow_id': tvshow_id,
                'video_id': video_id,
                'image_key':image_key
            }
        )
        return create_response(201, {'message': 'Episode created successfully!'})
    except ClientError as e:
        return create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])