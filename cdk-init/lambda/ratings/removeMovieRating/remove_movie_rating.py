import json
import boto3
import logging
from shared.utils import create_response

def remove_rating(event, context):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Movies')

    try:
        # Extract movie_id and email from query string parameters
        movie_id = event['queryStringParameters']['movie_id']
        email = event['queryStringParameters']['email']
    except Exception as e:
        return create_response(400, {'message': 'Invalid input'})

    try:
        # Check if the rating exists
        get_response = table.get_item(
            Key={'id': movie_id},
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
            Key={'id': movie_id},
            UpdateExpression="REMOVE #rating.#email",
            ExpressionAttributeNames={
                '#rating': 'rating',
                '#email': email
            },
            ReturnValues="UPDATED_NEW"
        )

        updated_rating = response.get('Attributes', {}).get('rating', {})

        return create_response(200, {'message': 'Rating removed successfully', 'updated_rating': updated_rating})
    except Exception as e:
        return create_response(500, {'message': f'Error removing rating: {str(e)}'})

# Lambda handler
def lambda_handler(event, context):
    if event['httpMethod'] == 'DELETE':
        return remove_rating(event, context)
    else:
        return create_response(405, {'message': 'Method Not Allowed'})
