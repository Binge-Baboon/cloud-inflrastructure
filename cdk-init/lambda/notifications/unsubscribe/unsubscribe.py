import os
import json
import boto3
from shared.utils import create_response
from shared.utils import get_topic_arn

sns_client = boto3.client('sns')

def get_subscription_arn(topic_arn, email):
    subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
    for subscription in subscriptions['Subscriptions']:
        if subscription['Endpoint'] == email:
            return subscription['SubscriptionArn']
    return None


def handler(event, context):
    body = json.loads(event['body'])
    topic_name = body.get('topic_name')
    email = body.get('email')

    if not topic_name or not email:
        return create_response(400, {'message': 'Topic name and email are required'})

    topic_arn = get_topic_arn(topic_name)
    if not topic_arn:
        return create_response(400, {'message': f'Topic {topic_name} does not exist.'})

    subscription_arn = get_subscription_arn(topic_arn, email)
    if not subscription_arn:
        return create_response(400, {'message': f'Subscription for {email} does not exist on topic {topic_name}.'})

    sns_client.unsubscribe(
        SubscriptionArn=subscription_arn
    )

    return create_response(200, {'message': f'Successfully unsubscribed {email} from topic {topic_name}.'})

