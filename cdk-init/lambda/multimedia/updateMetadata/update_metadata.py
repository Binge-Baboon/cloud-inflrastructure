import json
import os
import logging
import boto3
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    movies_table_name = os.environ['MOVIES_TABLE_NAME']

    for record in event['Records']:
        key = record['s3']['object']['key']

        if key.startswith('videos/'):
            video_id = extract_video_id(key)
            metadata = analyze_video(bucket_name, key)
            logger.info('Metadata: %s', json.dumps(metadata))

            # Update the metadata in the DynamoDB table
            update_metadata_in_dynamodb(movies_table_name, video_id, metadata)


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

def extract_video_id(key):
    # Assuming the key format is 'videos/<id>/filename'
    parts = key.split('/')
    if len(parts) >= 3:
        return parts[1]
    return None

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
