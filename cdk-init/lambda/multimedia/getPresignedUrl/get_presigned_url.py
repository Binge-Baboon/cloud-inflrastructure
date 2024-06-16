import json
import os
import boto3
import logging

s3 = boto3.client('s3')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from shared.utils import create_response

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    key = event['queryStringParameters']['key']

    try:
        # Generate a pre-signed URL for the S3 object
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )

        return create_response(200, {'url': url})

    except Exception as e:
        logger.error('Error generating pre-signed URL: %s', e)
        return create_response(500, {'error': str(e)})

