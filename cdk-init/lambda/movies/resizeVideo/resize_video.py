import json
import boto3
import cv2
from shared.utils import create_response

s3_client = boto3.client('s3')


def resize(event, context):
    bucket = "binge-baboon"
    body = json.loads(event['body'])
    movie_id = body.get("id")
    key = "videos/" + movie_id + "/" + body.get("image_key")

    download_path = f'/tmp/{key}'

    s3_client.download_file(bucket, key, download_path)

    output_path = f'/tmp/resized-{key}'

    cap = cv2.VideoCapture(download_path)

    if not cap.isOpened():
        return create_response(500, 'Error opening video file')


    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if original_height == 720:
        target_resolution = (720, 480)
    elif original_height == 480:
        target_resolution = (640, 360)
    elif original_height == 360:
        return create_response(200, 'Video is already at the lowest resolution (360p)')
    else:
        return create_response(200, 'Video resolution is not 720p, 480p, or 360p')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), target_resolution)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, target_resolution)
        out.write(resized_frame)

    cap.release()
    out.release()

    resized_key = f'videos/{movie_id}/{target_resolution[1]}.mp4'
    s3_client.upload_file(output_path, bucket, resized_key)

    return create_response(200, 'Video resized and uploaded successfully!')
