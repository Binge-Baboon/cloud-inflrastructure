import json
import os
import boto3
from shared.utils import create_response

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']


def handler(event, context):
    key_prefix = event['queryStringParameters']['key']

    try:
        # List all objects with the given prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)

        # Check if the response contains any objects
        if 'Contents' in response:
            # Extract the keys of the objects
            keys = [item['Key'] for item in response['Contents']]

            # Create a list of dictionaries with the keys for deletion
            delete_keys = [{'Key': key} for key in keys]

            # Delete the objects
            s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_keys}
            )
            message = 'All objects in the specified folder were deleted successfully'
        else:
            message = 'No objects found in the specified folder'
    except Exception as e:
        print(f"Error deleting objects in folder {key_prefix}: {e}")
        message = f"Error deleting objects in folder: {e}"

    return create_response(200, {"message": message})

