import json
import subprocess
import os
import boto3

s3 = boto3.client('s3')

def resize(event, context):
    bucket = "binge-baboon"

    original_key = event['original_key']
    target_resolution = event['target_resolution']
    video_type, video_id, episode_number = extract_video_details(original_key)


    if video_type == 'movies':
        output_prefix = "videos/movies" + video_id + "/"
    elif video_type == 'tv-show':
        output_prefix = "videos/tv-show/" + video_id + "/" + episode_number + "/"


    body = json.loads(event['body'])
    movie_id = body.get("id")
    video_key = body.get("video_key")
    key = "videos/" + movie_id + "/" + video_key


    download_dir = '/tmp/videos'
    os.makedirs(download_dir, exist_ok=True)

    download_path = os.path.join(download_dir, video_key)
    s3.download_file(bucket, key, download_path)

    output_path = f'/tmp/videos/480.mp4'

    cmd = f'/opt/bin/ffmpeg -i {download_path} -vf "scale={720}:{480}" -c:a copy {output_path}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error getting video information with ffprobe',
                                'message': f'{result.stderr}'})
        }
    else:
        # Upload the resized video back to S3
        transcoded_key = f'{output_prefix}{480}.mp4'
        s3.upload_file(output_path, bucket, transcoded_key)



    os.remove(download_path)

    return {
        'statusCode': 200,
        'transcoded_key': transcoded_key,
        'body': json.dumps(f'Video resized to lower resolutions and uploaded successfully')
    }

def extract_video_details(key):
    # Assuming the key format is 'videos/<type>/<id>/filename' or 'videos/tv-show/<id>/<episode>/filename'
    parts = key.split('/')
    if len(parts) >= 3:
        video_type = parts[1]
        video_id = parts[2]
        episode_number = None
        if video_type == 'tv-show' and len(parts) >= 4:
            episode_number = parts[3]
        return video_type, video_id, episode_number
    return None, None, None