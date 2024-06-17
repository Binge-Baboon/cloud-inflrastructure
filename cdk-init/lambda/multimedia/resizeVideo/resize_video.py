import json
import subprocess
import os
import boto3

s3 = boto3.client('s3')

def resize(event, context):
    bucket = "binge-baboon"
    body = json.loads(event['body'])
    movie_id = body.get("id")
    video_key = body.get("video_key")
    key = "videos/" + movie_id + "/" + video_key

    output_prefix = "videos/" + movie_id + "/"
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
        resized_key = f'{output_prefix}{480}.mp4'
        s3.upload_file(output_path, bucket, resized_key)


    # target_resolutions = []
    # if original_height > 720:
    #     target_resolutions = [(1080, 720), (720, 480), (640, 360)]
    # elif original_height == 720:
    #     target_resolutions = [(720, 480), (640, 360)]
    # elif original_height > 360:
    #     target_resolutions = [(640, 360)]
    # else:
    #     return {
    #         'statusCode': 400,
    #         'body': json.dumps('Video resolution is too low to resize')
    #     }
    #
    # resized_videos = []
    # for resolution in target_resolutions:
    #     width, height = resolution
    #     output_path = f'/tmp/{output_prefix}/{height}.mp4'
    #
    #     #cmd = f'/opt/bin/ffmpeg -i {download_path} -vf "scale=-1:{height}" -c:a copy {output_path}'
    #     cmd = f'/opt/bin/ffmpeg -i {download_path} -vf "scale={width}:{height}" -c:a copy {output_path}'
    #     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    #     if result.returncode != 0:
    #         return {
    #             'statusCode': 500,
    #             'body': json.dumps(f'Error resizing video to {height}p with ffmpeg: {result.stderr}')
    #         }
    #     else:
    #         # Upload the resized video back to S3
    #         resized_key = f'{output_prefix}/{height}.mp4'
    #         s3.upload_file(output_path, bucket, resized_key)
    #         resized_videos.append(resized_key)
    #     os.remove(output_path)
    os.remove(download_path)

    return {
        'statusCode': 200,
        'body': json.dumps(f'Video resized to lower resolutions and uploaded successfully')
    }
