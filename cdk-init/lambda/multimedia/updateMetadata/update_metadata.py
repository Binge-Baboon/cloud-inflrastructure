import json
import os
import logging
import boto3
from botocore.exceptions import ClientError
import decimal
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    movies_table_name = os.environ['MOVIES_TABLE_NAME']
    tv_shows_table_name = os.environ['TV_SHOWS_TABLE_NAME']

    for record in event['Records']:
        # Extract S3 event data from the message body
        message_body = json.loads(record['body'])

        logger.info(f"Message body: {json.dumps(message_body)}")

        s3_event = message_body['Records'][0]['s3']

        # Extract bucket name and object key from the S3 event
        bucket_name = s3_event['bucket']['name']
        key = s3_event['object']['key']

        if key.startswith('videos/'):
            video_type, video_id, episode_number = extract_video_details(key)
            metadata = analyze_video(bucket_name, key)
            logger.info('Metadata: %s', json.dumps(metadata))

            if video_type == 'movies':
                update_metadata_in_dynamodb(movies_table_name, video_id, metadata)
            elif video_type == 'tv-show':
                update_tv_show_metadata_in_dynamodb(tv_shows_table_name, video_id, episode_number, metadata)

def analyze_video(bucket, key):
    # Get the object metadata
    response = s3.head_object(Bucket=bucket, Key=key)

    # Extract the required metadata
    metadata = {
        "dataType": key.split('.')[-1],
        "resolution": key.split('.')[0].split('/')[-1],
        "size": str(round(response['ContentLength'] / (1024 * 1024), 3)),  # Size in MB
        "created": response['LastModified'].isoformat(),
        "modified": response['LastModified'].isoformat()
    }

    return metadata

def extract_video_details(key):
    # Assuming the key format is 'videos/<type>/<id>/filename' or 'videos/tv-show/<id>/<episode>/filename'
    parts = key.split('/')
    if len(parts) >= 3:
        video_type = parts[1]
        video_id = parts[2]
        episode_number = None
        if video_type == 'tv-show' and len(parts) >= 4:
            episode_number = parts[3]
        return video_type, video_id, episode_number
    return None, None, None

def update_metadata_in_dynamodb(table_name, video_id, metadata):
    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'id': {'S': video_id}
            },
            UpdateExpression="SET metadata.#resolution = :metadata",
            ExpressionAttributeNames={
                "#resolution": metadata['resolution']
            },
            ExpressionAttributeValues={
                ":metadata": {
                    'M': {
                        'dataType': {'S': metadata['dataType']},
                        'size': {'S': metadata['size']},
                        'created': {'S': metadata['created']},
                        'modified': {'S': metadata['modified']}
                    }
                }
            }
        )
        logger.info('UpdateItem succeeded: %s', json.dumps(response))
    except Exception as e:
        logger.error('Error updating item in DynamoDB: %s', e)

def update_tv_show_metadata_in_dynamodb(table_name, tv_show_id, episode_number, metadata):
    try:
        res = metadata['resolution']
        logger.info(f'Episode number: {str(episode_number)}')
        logger.info(f'Resolution: {str(res)}')

        # Step 1: Ensure the episodes map exists
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'id': {'S': tv_show_id}
            },
            UpdateExpression="SET #episodes = if_not_exists(#episodes, :empty_map)",
            ExpressionAttributeNames={
                "#episodes": "episodes"
            },
            ExpressionAttributeValues={
                ":empty_map": {'M': {}}
            }
        )

        # Step 2: Ensure the specific episode map exists
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'id': {'S': tv_show_id}
            },
            UpdateExpression=f"SET episodes.#episode = if_not_exists(#episode, :empty_map)",
            ExpressionAttributeNames={
                "#episode": str(episode_number)
            },
            ExpressionAttributeValues={
                ":empty_map": {'M': {}}
            }
        )

        # Step 3: Ensure the specific resolution map exists
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'id': {'S': tv_show_id}
            },
            UpdateExpression=f"SET episodes.#episode.#res = if_not_exists(#res, :empty_map)",
            ExpressionAttributeNames={
                "#episode": str(episode_number),
                "#res": metadata['resolution']
            },
            ExpressionAttributeValues={
                ":empty_map": {'M': {}}
            }
        )

        # Step 4: Update the resolution metadata
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'id': {'S': tv_show_id}
            },
            UpdateExpression=f"SET episodes.#episode.#res = :res",
            ExpressionAttributeNames={
                "#episode": str(episode_number),
                "#res": metadata['resolution']
            },
            ExpressionAttributeValues={
                ":res": {
                    'M': {
                        'dataType': {'S': metadata['dataType']},
                        'size': {'S': metadata['size']},
                        'created': {'S': metadata['created']},
                        'modified': {'S': metadata['modified']}
                    }
                }
            },
            ReturnValues="UPDATED_NEW"
        )

        logger.info('UpdateItem succeeded: %s', json.dumps(response))
    except ClientError as e:
        logger.error('Error updating item in DynamoDB: %s', e)