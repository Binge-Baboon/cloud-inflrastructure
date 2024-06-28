import json
import boto3
import logging
from botocore.exceptions import ClientError
from shared.utils import create_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def add_tv_show_rating(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    try:
        body = json.loads(event['body'])
        email = body['email']
        tv_show_id = body['tv_show_id']
        rating = body['rating']
    except Exception as e:
        logger.error(f'Failed to parse request body: {str(e)}')
        return create_response(400, {'message': 'Invalid input'})

    if not (1 <= rating <= 5):
        logger.warning('Invalid rating value provided')
        return create_response(400, {'message': 'Rating must be between 1 and 5'})

    try:
        # Step 1: Check if the tvShowRatings attribute exists
        item = table.get_item(Key={'email': email}).get('Item')
        if not item or 'tvShowRatings' not in item:
            # Initialize tvShowRatings if it doesn't exist
            initial_ratings = {tv_show_id: rating}
            table.update_item(
                Key={'email': email},
                UpdateExpression="SET tvShowRatings = :ratings",
                ExpressionAttributeValues={':ratings': initial_ratings},
                ReturnValues="UPDATED_NEW"
            )
        else:
            # Step 2: Update the specific TV show rating
            table.update_item(
                Key={'email': email},
                UpdateExpression="SET tvShowRatings.#tv_show_id = :rating",
                ExpressionAttributeNames={'#tv_show_id': tv_show_id},
                ExpressionAttributeValues={':rating': rating},
                ReturnValues="UPDATED_NEW"
            )

        logger.info(f'Rating added/updated for email: {email}, tv_show_id: {tv_show_id}, rating: {rating}')

        return create_response(200, {'message': 'Rating added/updated successfully'})

    except ClientError as e:
        logger.error(f'ClientError updating rating: {str(e)}')
        return create_response(500, {'message': f'Error updating rating: {str(e)}'})

    except Exception as e:
        logger.error(f'Error updating rating: {str(e)}')
        return create_response(500, {'message': f'Error updating rating: {str(e)}'})
