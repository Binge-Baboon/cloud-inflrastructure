import json
import boto3

sns_client = boto3.client('sns')
def create_response(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
        'body': json.dumps(body, default=str)
    }

def get_topic_arn(topic_name):
    topics = sns_client.list_topics()
    for topic in topics['Topics']:
        if topic_name in topic['TopicArn']:
            return topic['TopicArn']
    return None