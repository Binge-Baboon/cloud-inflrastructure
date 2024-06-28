import json
import boto3
import logging
from botocore.exceptions import ClientError
from shared.utils import create_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def remove_tv_show_rating(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    try:
        email = event['queryStringParameters']['email']
        tv_show_id = event['queryStringParameters']['tv_show_id']
    except KeyError as e:
        error_message = f'Missing query parameter: {str(e)}'
        logger.error(error_message)
        return create_response(400, {'messacge': error_message})

    try:
        # Check if the tvShowRatings attribute exists before removing
        item = table.get_item(Key={'email': email}).get('Item')
        if not item or 'tvShowRatings' not in item or tv_show_id not in item['tvShowRatings']:
            error_message = 'TV show rating not found for the given user'
            logger.warning(error_message)
            return create_response(404, {'message': error_message})

        # Perform the remove operation
        response = table.update_item(
            Key={'email': email},
            UpdateExpression="REMOVE tvShowRatings.#tv_show_id",
            ExpressionAttributeNames={'#tv_show_id': tv_show_id},
            ReturnValues="UPDATED_NEW"
        )

        logger.info(f'Rating removed successfully for email: {email}, tv_show_id: {tv_show_id}')
        return create_response(200, {'message': 'Rating removed successfully',
                                     'updated_ratings': response.get('Attributes', {}).get('tvShowRatings')})

    except ClientError as e:
        logger.error(f'ClientError removing rating: {str(e)}')
        return create_response(500, {'message': f'Error removing rating: {str(e)}'})

    except Exception as e:
        logger.error(f'Error removing rating: {str(e)}')
        return create_response(500, {'message': f'Error removing rating: {str(e)}'})
