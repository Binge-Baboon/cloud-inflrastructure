import json
import boto3
import logging
from shared.utils import create_response
from shared.utils import get_topic_arn

# Initialize boto3 clients
sns_client = boto3.client('sns')
lambda_client = boto3.client('lambda')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']

            logger.info(f"New image: {new_image}")

            # Extract relevant information from the new image
            actors = [actor['S'] for actor in new_image.get('actors', {}).get('L', [])]
            directors = [director['S'] for director in new_image.get('directors', {}).get('L', [])]
            genres = [genre['S'] for genre in new_image.get('genres', {}).get('L', [])]

            logger.info(f"actors: {actors}")
            logger.info(f"directors: {directors}")
            logger.info(f"genres: {genres}")

            # Notify for each actor
            for actor in actors:
                notify(actor, 'actor')

            # Notify for each director
            for director in directors:
                notify(director, 'director')

            # Notify for each genre
            for genre in genres:
                notify(genre, 'genre')

    return create_response(200, {'message': 'Notifications processed successfully.'})


def notify(subject, subject_type):
    topic_name = f"{subject_type}-{subject}"
    message = f"New content available featuring {subject_type}: {subject}."

    logger.info(f"topic_name: {topic_name}")

    if not topic_name:
        return create_response(400, {'message': 'Topic name is required'})

    topic_arn = get_topic_arn(topic_name)
    if not topic_arn:
        return create_response(200, {'message': f'Topic {topic_name} does not exist. No notification sent.'})

    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message
    )

    logger.info(f"Notification sent for {subject_type}: {subject}")

    return create_response(200, {'message': 'Notification sent!'})
