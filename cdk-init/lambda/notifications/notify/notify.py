import os
import json
import boto3
from shared.utils import create_response
from shared.utils import get_topic_arn


sns_client = boto3.client('sns')

def handler(event, context):
    body = json.loads(event['body'])
    topic_name = body.get('topic_name')
    message = body.get('message')
    if not topic_name:
        return create_response(400, {'message': 'Topic name is required'})

    topic_arn = get_topic_arn(topic_name)
    if not topic_arn:
        return create_response(200, {'message': f'Topic {topic_name} does not exist. No notification sent.'})

    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message
    )

    return create_response(200, {'message': 'Notification sent!'})
