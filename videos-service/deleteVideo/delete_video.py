import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def delete(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Videos')

    video_id = event['pathParameters']['id']

    try:
        table.delete_item(
            Key={
                'id': int(video_id)
            }
        )
        return create_response(200, {'message': f'Video with ID {video_id} deleted successfully'})
    except ClientError as e:
        return create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])
