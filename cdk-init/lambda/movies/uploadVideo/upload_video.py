import json
import boto3
from shared.utils import create_response

s3_client = boto3.client('s3')


def upload(event, context):
    bucket_name = 'binge-baboon'
    folder_name = 'videos'
    file_name = event['pathParameters']['id']
    expiration = 3600

    presigned_url = s3_client.generate_presigned_url('put_object',
                                                     Params={'Bucket': bucket_name,
                                                             'Key': f'{folder_name}/{file_name}'},
                                                     ExpiresIn=expiration)

    return create_response(200,{'presigned_url': presigned_url})
