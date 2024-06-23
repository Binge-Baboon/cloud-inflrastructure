import json
import boto3
import logging
from shared.utils import create_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def remove_tv_show_rating(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TvShows')

    try:
        # Extract tv_show_id and email from query string parameters
        tv_show_id = event['queryStringParameters']['tv_show_id']
        email = event['queryStringParameters']['email']
    except KeyError as e:
        error_message = f'Missing query parameter: {str(e)}'
        logger.error(error_message)
        return create_response(400, {'message': error_message})

    try:
        # Check if the rating exists
        get_response = table.get_item(
            Key={'id': tv_show_id},
            ProjectionExpression="#rating.#email",
            ExpressionAttributeNames={
                '#rating': 'rating',
                '#email': email
            }
        )

        if 'Item' not in get_response or 'rating' not in get_response['Item'] or email not in get_response['Item']['rating']:
            return create_response(404, {'message': 'Rating not found'})

        # Remove the specific user's rating
        response = table.update_item(
            Key={'id': tv_show_id},
            UpdateExpression="REMOVE #rating.#email",
            ExpressionAttributeNames={
                '#rating': 'rating',
                '#email': email
            },
            ReturnValues="UPDATED_NEW"
        )

        updated_rating = response.get('Attributes', {}).get('rating', {})

        logger.info(f'Rating removed successfully for TV show ID: {tv_show_id}, email: {email}')

        return create_response(200, {'message': 'Rating removed successfully', 'updated_rating': updated_rating})

    except Exception as e:
        logger.error(f'Error removing rating: {str(e)}')
        return create_response(500, {'message': f'Error removing rating: {str(e)}'})

# Lambda handler
def lambda_handler(event, context):
    if event['httpMethod'] == 'DELETE':
        return remove_tv_show_rating(event, context)
    else:
        return create_response(405, {'message': 'Method Not Allowed'})
