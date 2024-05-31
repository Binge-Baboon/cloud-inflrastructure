import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def update(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Episodes')

    data = json.loads(event['body'])
    episode_id = event['pathParameters']['id']

    update_expression = "SET "
    expression_attribute_values = {}

    if 'title' in data:
        update_expression += "title = :title, "
        expression_attribute_values[':title'] = data['title']

    if 'description' in data:
        update_expression += "description = :description, "
        expression_attribute_values[':description'] = data['description']

    if 'season' in data:
        update_expression += "season = :season, "
        expression_attribute_values[':season'] = data['season']

    if 'episode' in data:
        update_expression += "episode = :episode, "
        expression_attribute_values[':episode'] = data['episode']

    if 'tvshow_id' in data:
        update_expression += "tvshow_id = :tvshow_id, "
        expression_attribute_values[':tvshow_id'] = data['tvshow_id']

    if 'video_id' in data:
        update_expression += "video_id = :video_id, "
        expression_attribute_values[':video_id'] = data['video_id']

    if 'image_key' in data:
        update_expression += "image_key = :image_key, "
        expression_attribute_values[':image_key'] = data['image_key']

    update_expression = update_expression.rstrip(', ')

    try:
        table.update_item(
            Key={
                'id': int(episode_id)
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return create_response(200, {'message': 'Episode updated successfully!'})

    except ClientError as e:
        create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])
