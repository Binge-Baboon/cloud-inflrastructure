from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    Duration,
    Stack,
    CfnOutput,
    Aws,
    aws_s3 as s3,
    RemovalPolicy
)
from constructs import Construct

from cdk_init.cdk_init_stack import BingeBaboonServiceStack
from movie_service.movie_service_stack import MoviesServiceStack

class MultimediaServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, movies_stack: MoviesServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer


        bucket_name = "binge-baboon"
        s3_bucket = s3.Bucket(self,
                           "BingeBaboonBucket",
                           bucket_name=bucket_name,
                           cors=[
                               s3.CorsRule(
                                   allowed_headers=["*"],
                                   allowed_methods=[
                                       s3.HttpMethods.GET,
                                       s3.HttpMethods.PUT,
                                       s3.HttpMethods.POST,
                                   ],
                                   allowed_origins=["*"],
                                   exposed_headers=[]
                               )
                           ]
                           )

        lambda_env = {
            "BUCKET_NAME": bucket_name
        }

        resize_video_lambda = _lambda.Function(self, "ResizeVideoFunction",
                                               runtime=_lambda.Runtime.PYTHON_3_12,
                                               handler="resizeVideo/resize_video.resize",
                                               code=_lambda.Code.from_asset("lambda/multimedia"),
                                               memory_size=128,
                                               timeout=Duration.seconds(10),
                                               environment=lambda_env
                                               )

        upload_video_lambda = _lambda.Function(self, "UploadVideoFunction",
                                               runtime=_lambda.Runtime.PYTHON_3_12,
                                               handler="uploadVideo/upload_video.upload",
                                               code=_lambda.Code.from_asset("lambda/multimedia"),
                                               memory_size=128,
                                               timeout=Duration.seconds(10),
                                               environment=lambda_env
                                               )

        upload_image_lambda = _lambda.Function(self, "UploadImageFunction",
                                               runtime=_lambda.Runtime.PYTHON_3_12,
                                               handler="uploadImage/upload_image.upload",
                                               code=_lambda.Code.from_asset("lambda/multimedia"),
                                               memory_size=128,
                                               timeout=Duration.seconds(10),
                                               environment=lambda_env,
                                               layers=[_lambda.LayerVersion.from_layer_version_arn(self, 'Pillow',
                                                                                                   'arn:aws:lambda:eu-central-1:770693421928:layer:Klayers-p312-Pillow:2')]
                                               )


        video_resource = api.root.add_resource("videos")

        video_resource.add_method("PUT", apigateway.LambdaIntegration(resize_video_lambda),
                                  authorization_type=apigateway.AuthorizationType.COGNITO,
                                  authorizer=authorizer,
                                  # api_key_required=True
                                  )

        videos_resource = video_resource.add_resource("upload")

        videos_resource.add_method("POST", apigateway.LambdaIntegration(upload_video_lambda),
                                   authorization_type=apigateway.AuthorizationType.COGNITO,
                                   authorizer=authorizer,
                                   # api_key_required=True
                                   )

        image_resource = api.root.add_resource("images")
        image_resource.add_method("POST", apigateway.LambdaIntegration(upload_image_lambda),
                                  authorization_type=apigateway.AuthorizationType.COGNITO,
                                  authorizer=authorizer,
                                  # api_key_required=True
                                  )


        # Grant Lambda functions permissions to interact with S3
        s3_bucket.grant_read_write(resize_video_lambda)
        s3_bucket.grant_read_write(upload_video_lambda)
        s3_bucket.grant_read_write(upload_image_lambda)

