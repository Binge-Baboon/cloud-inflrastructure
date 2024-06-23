import json
import boto3
import logging
from shared.utils import create_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def remove_movie_rating(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    # Extract parameters from query string
    try:
        email = event['queryStringParameters']['email']
        movie_id = event['queryStringParameters']['movie_id']
    except KeyError as e:
        error_message = f'Missing query parameter: {str(e)}'
        logger.error(error_message)
        return create_response(400, {'message': error_message})

    try:
        # Check if the movieRatings attribute exists before removing
        item = table.get_item(Key={'email': email}).get('Item')
        if not item or 'movieRatings' not in item or movie_id not in item['movieRatings']:
            error_message = 'Movie rating not found for the given user'
            logger.warning(error_message)
            return create_response(404, {'message': error_message})

        # Perform the remove operation
        response = table.update_item(
            Key={'email': email},
            UpdateExpression="REMOVE movieRatings.#movie_id",
            ExpressionAttributeNames={'#movie_id': movie_id},
            ReturnValues="UPDATED_NEW"
        )

        logger.info(f'Rating removed successfully for email: {email}, movie_id: {movie_id}')
        return create_response(200, {'message': 'Rating removed successfully',
                                     'updated_ratings': response.get('Attributes', {}).get('movieRatings')})

    except Exception as e:
        error_message = f'Error removing rating: {str(e)}'
        logger.error(error_message)
        return create_response(500, {'message': error_message})
