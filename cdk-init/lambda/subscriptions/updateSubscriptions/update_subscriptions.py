import json
import boto3
import logging
from shared.utils import create_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info('Event: %s', json.dumps(event))

    dynamodb = boto3.resource('dynamodb')
    actors_table = dynamodb.Table('Actors')
    directors_table = dynamodb.Table('Directors')
    genres_table = dynamodb.Table('Genres')

    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            logger.info('NewImage: %s', json.dumps(new_image))

            try:
                movie = {
                    # 'id': new_image['id']['S'],
                    # 'title': new_image['title']['S'],
                    # 'description': new_image['description']['S'],
                    # 'rating': new_image['rating']['M'],
                    'genres': [genre['S'] for genre in new_image['genres']['L']],
                    'actors': [actor['S'] for actor in new_image['actors']['L']],
                    'directors': [director['S'] for director in new_image['directors']['L']],
                    # 'metadata': new_image['metadata']['M']
                }
            except KeyError as e:
                logger.error('KeyError: %s', e)
                continue

            for actor in movie['actors']:
                # Check if actor exists in Actors table, if not, add them
                if not actors_table.get_item(Key={'name': actor}).get('Item'):
                    actors_table.put_item(Item={'name': actor})

            for director in movie['directors']:
                # Check if director exists in Directors table, if not, add them
                if not directors_table.get_item(Key={'name': director}).get('Item'):
                    directors_table.put_item(Item={'name': director})

            for genre in movie['genres']:
                # Check if genre exists in Genres table, if not, add them
                if not genres_table.get_item(Key={'genre': genre}).get('Item'):
                    genres_table.put_item(Item={'genre': genre})

    return create_response(200, {'message': 'Processed record successfully'})
