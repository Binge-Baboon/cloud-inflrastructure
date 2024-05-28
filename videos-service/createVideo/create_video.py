import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def create(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Videos')

    data = json.loads(event['body'])
    movie_id = data['id']
    size = data['size']
    datatype = data['datatype']
    modified = data['modified']
    created = data['created']
    s3key = data['s3key']

    try:
        table.put_item(
            Item={
                'id': movie_id,
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