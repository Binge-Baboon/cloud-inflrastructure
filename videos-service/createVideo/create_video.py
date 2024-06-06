import json
import base64
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')

    table = dynamodb.Table('Videos')
    bucket_name = 'binge-baboon-videos'

    data = json.loads(event['body'])
    video_id = data['id']
    size = data['size']
    datatype = data['datatype']
    modified = data['modified']
    created = data['created']
    video_data = data['video_data']
    s3key = f"{video_id}.mp4"


    try:
        video_binary = base64.b64decode(video_data)

        s3.put_object(Bucket=bucket_name, Key=s3key, Body=video_binary, ContentType='video/mp4')


        table.put_item(
            Item={
                'id': video_id,
                'size': size,
                'datatype': datatype,
                'modified': modified,
                'created': created,
                's3key': s3key
            }
        )
        return create_response(201, {'message': 'Video created successfully!'})
    except ClientError as e:
        return create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])