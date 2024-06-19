import json

def handler(event, context):
    key = event['key']
    resolutions = [720, 480, 360]

    return {
        'original_key': key,
        'resolutions': resolutions
    }
