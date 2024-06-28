import json
import os
import boto3

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']


def handler(event, context):
    print("Event: ", json.dumps(event))

    for record in event['Records']:
        if record['eventName'] == 'REMOVE':
            # Handle delete event
            deleted_item = record['dynamodb']['OldImage']
            tv_show_id = deleted_item['id']['S']
            print(f"Handling delete for TV show ID: {tv_show_id}")

            # Delete TV show data
            delete_tv_show_data(deleted_item, tv_show_id)

    return {
        'statusCode': 200,
        'body': json.dumps('Delete TV show data handler executed successfully')
    }


def delete_tv_show_data(deleted_item, tv_show_id):
    # Extract episodes map
    episodes = deleted_item['episodes']['M']
    for episode_number, episode_data in episodes.items():
        episode_metadata = episode_data['M']
        for resolution, info in episode_metadata.items():
            data_type = info['M']['dataType']['S']
            video_path = f"videos/tv-show/{tv_show_id}/{episode_number}/{resolution}.{data_type}"
            print(f"Deleting video at path: {video_path}")
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=video_path)
            except Exception as e:
                print(f"Error deleting video at path {video_path}: {e}")

    # Delete associated image
    image_path = f"images/{tv_show_id}.jpg"
    print(f"Deleting image at path: {image_path}")
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=image_path)
    except Exception as e:
        print(f"Error deleting image at path {image_path}: {e}")
