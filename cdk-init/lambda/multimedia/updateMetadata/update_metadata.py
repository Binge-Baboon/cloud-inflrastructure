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

    bucket_name = os.environ['BUCKET_NAME']
    movies_table_name = os.environ['MOVIES_TABLE_NAME']
    tv_shows_table_name = os.environ['TV_SHOWS_TABLE_NAME']

    for record in event['Records']:
        key = record['s3']['object']['key']

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
        # Attempt to update the DynamoDB item with nested attributes
        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'id': {'S': tv_show_id}
            },
            UpdateExpression="SET episodes.#episode = :episode",
            ExpressionAttributeNames={
                "#episode": str(episode_number)
            },
            ExpressionAttributeValues={
                ":episode": {
                    'M': {
                        metadata['resolution']: {
                            'M': {
                                'dataType': {'S': metadata['dataType']},
                                'size': {'S': metadata['size']},
                                'created': {'S': metadata['created']},
                                'modified': {'S': metadata['modified']}
                            }
                        }
                    }
                }
            },
            ReturnValues="UPDATED_NEW"
        )
        logger.info('UpdateItem succeeded: %s', json.dumps(response))
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            # Handle case where nested attributes path is invalid; create 'episodes' and 'episode' attributes
            try:
                # Construct the ExpressionAttributeValues for nested attributes
                episodes_data = {
                    str(episode_number): {
                        metadata['resolution']: {
                            'dataType': metadata['dataType'],
                            'size': metadata['size'],
                            'created': metadata['created'],
                            'modified': metadata['modified']
                        }
                    }
                }

                # Update DynamoDB with the nested attributes
                response = dynamodb.update_item(
                    TableName=table_name,
                    Key={
                        'id': {'S': tv_show_id}
                    },
                    UpdateExpression="SET episodes = :episodes",
                    ExpressionAttributeValues={
                        ":episodes": {'M': episodes_data}
                    },
                    ReturnValues="UPDATED_NEW"
                )
                logger.info('UpdateItem succeeded (inner): %s', json.dumps(response))
            except Exception as inner_e:
                logger.error('Error updating item in DynamoDB (inner): %s', inner_e)
        else:
            logger.error('Error updating item in DynamoDB: %s', e)