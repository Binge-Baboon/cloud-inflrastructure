import json
import boto3
from shared.utils import create_response

def update(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Movies')

    body = json.loads(event['body'])
    movie_id = event['pathParameters']['id']

    update_expression = "set "
    expression_attribute_values = {}

    for key, value in body.items():
        update_expression += f"{key} = :{key}, "
        expression_attribute_values[f":{key}"] = value

    update_expression = update_expression.rstrip(", ")

    response = table.update_item(
        Key={
            'id': movie_id
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )

    return create_response(200, {'message': 'Movie updated successfully', 'attributes': response['Attributes']})
