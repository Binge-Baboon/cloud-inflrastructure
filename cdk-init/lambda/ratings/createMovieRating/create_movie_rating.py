import json
import boto3
import logging
from shared.utils import create_response

def add_or_update_rating(event, context):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Movies')

    try:
        body = json.loads(event['body'])
        movie_id = body['movie_id']
        email = body['email']
        rating = body['rating']
    except Exception as e:
        return create_response(400, {'message': 'Invalid input'})

    if not (1 <= rating <= 5):
        return create_response(400, {'message': 'Rating must be between 1 and 5'})

    try:
        # First, initialize the rating map if it doesn't exist
        response = table.update_item(
            Key={'id': movie_id},
            UpdateExpression="SET #rating = if_not_exists(#rating, :empty_map)",
            ExpressionAttributeNames={
                '#rating': 'rating'
            },
            ExpressionAttributeValues={
                ':empty_map': {}
            }
        )

        # Now, update the specific user's rating
        response = table.update_item(
            Key={'id': movie_id},
            UpdateExpression="SET #rating.#email = :rating",
            ExpressionAttributeNames={
                '#rating': 'rating',
                '#email': email
            },
            ExpressionAttributeValues={
                ':rating': rating
            },
            ReturnValues="UPDATED_NEW"
        )
        return create_response(200, {'message': 'Rating added/updated successfully', 'updated_rating': response['Attributes'].get('rating')})
    except Exception as e:
        return create_response(500, {'message': f'Error updating rating: {str(e)}'})
