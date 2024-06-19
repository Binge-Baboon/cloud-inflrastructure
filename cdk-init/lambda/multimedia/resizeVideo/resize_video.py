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

    resolutions = {
        720: 1080,
        480: 720,
        360: 480
    }

    if target_resolution not in resolutions.keys():
        resolution = [-1, target_resolution]
    else:
        resolution = [resolutions[target_resolution], target_resolution]

    output_prefix = ""
    if video_type == 'movies':
        output_prefix = "videos/movies" + video_id + "/"
    elif video_type == 'tv-show':
        output_prefix = "videos/tv-show/" + video_id + "/" + episode_number + "/"

    download_dir = '/tmp/videos'
    os.makedirs(download_dir, exist_ok=True)

    download_path = os.path.join(download_dir, original_key)
    s3.download_file(bucket, original_key, download_path)

    output_path = f'/tmp/videos/{resolution[1]}.mp4'

    cmd = f'/opt/bin/ffmpeg -i {download_path} -vf "scale={resolution[0]}:{resolution[1]}" -c:a copy {output_path}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error getting video information with ffprobe',
                                'message': f'{result.stderr}'})
        }
    else:
        transcoded_key = f'{output_prefix}{resolution[1]}.mp4'
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