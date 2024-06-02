import json
import boto3
import base64

from shared.utils import create_response


def get_one(event, context):
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')

    table = dynamodb.Table('Movies')
    bucket_name = 'binge-baboon-images'

    movie_id = event['pathParameters']['id']
    response = table.get_item(
        Key={
            'id': int(movie_id)
        }
    )

    if 'Item' in response:
        item = response['Item']
        if 'image_key' in item:
            image_key = item['image_key']
            try:
                s3_response = s3.get_object(Bucket=bucket_name, Key=image_key)
                image_data = s3_response['Body'].read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                item['image_data'] = image_base64
            except Exception as e:
                print(f"Error fetching image from S3: {e}")
                item['image_data'] = None
        return create_response(200, item)
    else:
        return create_response(404, {'message': 'Movie not found'})
