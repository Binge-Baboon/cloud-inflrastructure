import json
import boto3
from botocore.exceptions import ClientError

from shared.utils import create_response

def update(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Videos')

    data = json.loads(event['body'])
    movie_id = event['pathParameters']['id']

    update_expression = "SET "
    expression_attribute_values = {}


    if 'size' in data:
        update_expression += "size = :size, "
        expression_attribute_values[':size'] = data['sizes']

    if 'datatype' in data:
        update_expression += "datatype = :datatype, "
        expression_attribute_values[':datatype'] = data['datatype']

    if 'modified' in data:
        update_expression += "modified = :modified, "
        expression_attribute_values[':modified'] = data['modified']

    if 'created' in data:
        update_expression += "created = :created, "
        expression_attribute_values[':created'] = data['created']

    if 's3key' in data:
        update_expression += "s3key = :s3key, "
        expression_attribute_values[':s3key'] = data['s3key']

    update_expression = update_expression.rstrip(', ')

    try:
        table.update_item(
            Key={
                'id': int(movie_id)
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return create_response(200, {'message': 'Movie updated successfully!'})

    except ClientError as e:
        create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])
