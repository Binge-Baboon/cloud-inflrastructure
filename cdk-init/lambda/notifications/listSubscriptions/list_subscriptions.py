import boto3
import json
from botocore.exceptions import ClientError

sns_client = boto3.client('sns')
from shared.utils import create_response


def handler(event, context):
    email = event['queryStringParameters']['email']
    if not email:
        return create_response(400, {'message': 'Email parameter is required.'})

    try:
        subscriptions = get_subscriptions(email)
        return create_response(200, {'subscriptions': subscriptions})
    except ClientError as e:
        return create_response(500, {'message': str(e)})


def get_subscriptions(email):
    subscriptions = []
    next_token = None

    while True:
        if next_token:
            response = sns_client.list_subscriptions(NextToken=next_token)
        else:
            response = sns_client.list_subscriptions()

        for subscription in response['Subscriptions']:
            if subscription['Protocol'] == 'email' and subscription['Endpoint'] == email:
                subscriptions.append(subscription['TopicArn'])

        next_token = response.get('NextToken')
        if not next_token:
            break

    return subscriptions
