import json
import boto3
import base64

from shared.utils import create_response

def get_one(event, context):
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')

    table = dynamodb.Table('Videos')
    bucket_name = 'binge-baboon-videos'

    video_id = event['pathParameters']['id']
    response = table.get_item(
        Key={
            'id': int(video_id)
        }
    )
    if 'Item' in response:
        item = response['Item']
        if 's3key' in item:
            video_key = item['s3key']
            try:
                s3_response = s3.get_object(Bucket=bucket_name, Key=video_key)
                video_data = s3_response['Body'].read()
                image_base64 = base64.b64encode(video_data).decode('utf-8')
                item['video_data'] = image_base64
            except Exception as e:
                print(f"Error fetching video from S3: {e}")
                item['video_data'] = None
        return create_response(200, response['Item'])
    else:
        return create_response(404, {'message': 'Video not found'})
