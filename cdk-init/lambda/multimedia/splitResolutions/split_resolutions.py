import json

def handler(event, context):
    original_key = event['key']
    resolutions = ['720p', '480p', '360p']

    return {
        'statusCode': 200,
        'original_key': original_key,
        'resolutions': resolutions
    }