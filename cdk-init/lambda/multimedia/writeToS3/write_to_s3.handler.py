import boto3
import json

s3_client = boto3.client('s3')


def handler(event, context):
    transcoded_key = event['transcoded_key']

    bucket_name = 'binge-baboon'

    try:
        # Replace the following line with the actual code to upload the transcoded video to S3
        s3_client.put_object(Bucket=bucket_name, Key=transcoded_key, Body=b'Video content')
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }

    return {
        'statusCode': 200,
        'message': f'Successfully uploaded {transcoded_key} to {bucket_name}'
    }
