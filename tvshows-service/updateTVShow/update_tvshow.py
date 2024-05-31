import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def update(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TVShows')

    data = json.loads(event['body'])
    tvshow_id = event['pathParameters']['id']

    update_expression = "SET "
    expression_attribute_values = {}

    if 'title' in data:
        update_expression += "title = :title, "
        expression_attribute_values[':title'] = data['title']

    if 'description' in data:
        update_expression += "description = :description, "
        expression_attribute_values[':description'] = data['description']

    if 'genres' in data:
        update_expression += "genres = :genres, "
        expression_attribute_values[':genres'] = data['genres']

    if 'actors' in data:
        update_expression += "actors = :actors, "
        expression_attribute_values[':actors'] = data['actors']

    if 'directors' in data:
        update_expression += "directors = :directors, "
        expression_attribute_values[':directors'] = data['directors']

    if 'rating' in data:
        update_expression += "rating = :rating, "
        expression_attribute_values[':rating'] = data['rating']

    if 'image_key' in data:
        update_expression += "image_key = :image_key, "
        expression_attribute_values[':image_key'] = data['image_key']

    update_expression = update_expression.rstrip(', ')

    try:
        table.update_item(
            Key={
                'id': int(tvshow_id)
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return create_response(200, {'message': 'TVShow updated successfully!'})

    except ClientError as e:
        create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])
