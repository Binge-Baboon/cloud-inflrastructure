import json
import boto3
import logging
from shared.utils import create_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def add_or_update_tv_show_rating(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TvShows')

    try:
        body = json.loads(event['body'])
        tv_show_id = body['tv_show_id']
        email = body['email']
        rating = body['rating']
    except Exception as e:
        logger.error(f'Failed to parse request body: {str(e)}')
        return create_response(400, {'message': 'Invalid input'})

    if not (1 <= rating <= 5):
        logger.warning('Invalid rating value provided')
        return create_response(400, {'message': 'Rating must be between 1 and 5'})

    try:
        # First, initialize the rating map if it doesn't exist
        response = table.update_item(
            Key={'id': tv_show_id},
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
            Key={'id': tv_show_id},
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

        logger.info(f'Rating added/updated for TV show ID: {tv_show_id}, email: {email}, rating: {rating}')

        return create_response(200, {'message': 'Rating added/updated successfully', 'updated_rating': response['Attributes'].get('rating')})

    except Exception as e:
        logger.error(f'Error updating rating: {str(e)}')
        return create_response(500, {'message': f'Error updating rating: {str(e)}'})
