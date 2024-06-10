import json
import boto3
from botocore.exceptions import ClientError
from shared.utils import create_response

def download(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'binge-baboon-videos'

    video_id = event['pathParameters']['id']
    s3key = f"{video_id}.mp4"

    try:
        presigned_url = s3.generate_presigned_url('get_object',
                                                  Params={'Bucket': bucket_name, 'Key': s3key},
                                                  ExpiresIn=3600)

        return create_response(200, {'presigned_url': presigned_url})
    except ClientError as e:
        return create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])
