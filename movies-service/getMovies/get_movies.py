import json
import boto3
import base64

from shared.utils import create_response

def get_all(event, context):
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')

    table = dynamodb.Table('Movies')
    bucket_name = 'binge-baboon-images'  # replace with your S3 bucket name

    response = table.scan()
    movies = response['Items']

    for movie in movies:
        if 'image_key' in movie:
            image_key = movie['image_key']
            try:
                s3_response = s3.get_object(Bucket=bucket_name, Key=image_key)
                image_data = s3_response['Body'].read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                movie['image_data'] = image_base64
            except Exception as e:
                print(f"Error fetching image from S3 for movie {movie['id']}: {e}")
                movie['image_data'] = None
        else:
            movie['image_data'] = None

    return create_response(200, movies)
