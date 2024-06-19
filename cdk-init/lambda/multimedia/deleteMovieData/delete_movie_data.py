import json
import os
import boto3
from shared.utils import create_response

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']


def handler(event, context):
    print("Event: ", json.dumps(event))

    for record in event['Records']:
        if record['eventName'] == 'REMOVE':
            # Handle delete event
            deleted_item = record['dynamodb']['OldImage']
            movie_id = deleted_item['id']['S']
            print(f"Handling delete for movie ID: {movie_id}")

            # Delete associated videos based on metadata
            metadata = deleted_item['metadata']['M']
            for resolution, info in metadata.items():
                data_type = info['M']['dataType']['S']
                video_path = f"videos/movies/{movie_id}/{resolution}.{data_type}"
                print(f"Deleting video at path: {video_path}")
                try:
                    s3_client.delete_object(Bucket=bucket_name, Key=video_path)
                except Exception as e:
                    print(f"Error deleting video at path {video_path}: {e}")

            # Delete associated image
            image_path = f"images/{movie_id}.jpg"
            print(f"Deleting image at path: {image_path}")
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=image_path)
            except Exception as e:
                print(f"Error deleting image at path {image_path}: {e}")

    return create_response(200, {'message': "Delete movie data handler executed successfully"})

