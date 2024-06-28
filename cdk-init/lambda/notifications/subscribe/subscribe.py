import os
import json
import boto3
from shared.utils import create_response
from shared.utils import get_topic_arn

sns_client = boto3.client('sns')

def handler(event, context):
    body = json.loads(event['body'])
    topic_name = body.get('topic_name')
    email = body.get('email')

    if not topic_name or not email:
        return create_response(400, {'message': 'Topic name and email are required'})

    topic_arn = get_topic_arn(topic_name)
    if not topic_arn:
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']

    response = sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )

    return create_response(200, {'message': 'Subscription request sent! Please check your email to confirm.'})

