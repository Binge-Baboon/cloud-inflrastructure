import json
import boto3
import base64
from shared.utils import create_response
from PIL import Image
from botocore.exceptions import ClientError
from io import BytesIO

def upload(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'binge-baboon2'
    folder_name = 'images'
    body = json.loads(event['body'])
    movie_id = body.get('id')

    image_data = body.get('image_data')

    try:
        image_binary = base64.b64decode(image_data)
        with BytesIO(image_binary) as image_stream:
            with Image.open(image_stream) as im:
                rgb_im = im.convert('RGB')

                buffer = BytesIO()
                rgb_im.save(buffer, format='JPEG')
                buffer.seek(0)

                image_key = f"{folder_name}/{movie_id}.jpg"

                s3.put_object(Bucket=bucket_name, Key=image_key, Body=buffer, ContentType='image/jpeg')


        return create_response(201, {'message': 'Image added successfully!'})
    except ClientError as e:
        return create_response(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])
    except Exception as e:
        return create_response(500, str(e))
