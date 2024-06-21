import json
import boto3
from shared.utils import create_response

def add(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')

    body = json.loads(event['body'])
    email = body['email']
    id = body['id']
    type = body['type']



    user = table.get_item(
        Key={
            'email': email
        }
    )['Item']

    update_expression = "set "
    expression_attribute_values = {}

    key = 'watched'

    user[key][type].append(id)

    update_expression += f"{key} = :{key}, "
    expression_attribute_values[f":{key}"] = user[key]

    update_expression = update_expression.rstrip(", ")

    response = table.update_item(
        Key={
            'email': email
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )

    return create_response(200, {'message': 'User updated successfully', 'attributes': response['Attributes']})
