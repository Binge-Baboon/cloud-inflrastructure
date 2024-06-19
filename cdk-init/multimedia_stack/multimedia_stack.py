from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_lambda_event_sources as lambda_event_sources,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    Duration,
    Stack,
    CfnOutput,
    Aws,
    aws_sqs as sqs,
    aws_s3 as s3,
    RemovalPolicy,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_s3_notifications as s3_notifications
)
from constructs import Construct
import os

from cdk_init.cdk_init_stack import BingeBaboonServiceStack
from movie_service.movie_service_stack import MoviesServiceStack
from tvShowService.tv_show_service_stack import TvShowsServiceStack

class MultimediaServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, movies_stack: MoviesServiceStack, tv_shows_stack: TvShowsServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer
        movies_table = movies_stack.movies_table
        tv_shows_table = tv_shows_stack.tv_shows_table

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
            "BUCKET_NAME": bucket_name,
            "MOVIES_TABLE_NAME": movies_table.table_name,
            "TV_SHOWS_TABLE_NAME": tv_shows_table.table_name

        }


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

        update_metadata_lambda = _lambda.Function(self, "UpdateMetadataFunction",
                                                  runtime=_lambda.Runtime.PYTHON_3_12,
                                                  handler="updateMetadata/update_metadata.handler",
                                                  code=_lambda.Code.from_asset("lambda/multimedia"),
                                                  memory_size=128,
                                                  timeout=Duration.seconds(10),
                                                  environment=lambda_env
                                                  )

        get_presigned_url_lambda = _lambda.Function(self, "GetVideoFunction",
                                            runtime=_lambda.Runtime.PYTHON_3_12,
                                            handler="getPresignedUrl/get_presigned_url.handler",
                                            code=_lambda.Code.from_asset("lambda/multimedia"),
                                            memory_size=128,
                                            timeout=Duration.seconds(10),
                                            environment=lambda_env
                                            )

        delete_movie_data_lambda = _lambda.Function(self, "DeleteMovieDataFunction",
                                                    runtime=_lambda.Runtime.PYTHON_3_12,
                                                    handler="deleteMovieData/delete_movie_data.handler",
                                                    code=_lambda.Code.from_asset("lambda/multimedia"),
                                                    memory_size=128,
                                                    timeout=Duration.seconds(10),
                                                    environment=lambda_env
                                                    )

        delete_tv_show_data_lambda = _lambda.Function(self, "DeleteTvShowDataFunction",
                                                    runtime=_lambda.Runtime.PYTHON_3_12,
                                                    handler="deleteTvShowData/delete_tv_show_data.handler",
                                                    code=_lambda.Code.from_asset("lambda/multimedia"),
                                                    memory_size=128,
                                                    timeout=Duration.seconds(10),
                                                    environment=lambda_env
                                                    )

        delete_movie_data_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(
                movies_table,
                starting_position=_lambda.StartingPosition.LATEST,
            )
        )

        delete_tv_show_data_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(
                tv_shows_table,
                starting_position=_lambda.StartingPosition.LATEST,
            )
        )

        # Add the S3 event notification for update
        notification = s3_notifications.LambdaDestination(update_metadata_lambda)
        s3_bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, notification, s3.NotificationKeyFilter(prefix="videos/"))

        video_resource = api.root.add_resource("videos")
        presigned_url_resource = api.root.add_resource("presigned_url")

        presigned_url_resource.add_method("GET", apigateway.LambdaIntegration(get_presigned_url_lambda),
                                   authorization_type=apigateway.AuthorizationType.COGNITO,
                                   authorizer=authorizer,
                                   )

        videos_resource = video_resource.add_resource("upload")

        videos_resource.add_method("POST", apigateway.LambdaIntegration(upload_video_lambda),
                                   authorization_type=apigateway.AuthorizationType.COGNITO,
                                   authorizer=authorizer,
                                   )


        image_resource = api.root.add_resource("images")
        image_resource.add_method("POST", apigateway.LambdaIntegration(upload_image_lambda),
                                  authorization_type=apigateway.AuthorizationType.COGNITO,
                                  authorizer=authorizer,
                                  )

        # Grant Lambda functions permissions to interact with S3
        s3_bucket.grant_read_write(upload_video_lambda)
        s3_bucket.grant_read_write(upload_image_lambda)
        s3_bucket.grant_read_write(update_metadata_lambda)
        s3_bucket.grant_read(get_presigned_url_lambda)
        s3_bucket.grant_read_write(delete_movie_data_lambda)
        s3_bucket.grant_read_write(delete_tv_show_data_lambda)

        movies_table.grant_read_write_data(update_metadata_lambda)
        tv_shows_table.grant_read_write_data(update_metadata_lambda)

        movies_table.grant_stream_read(delete_movie_data_lambda)
        tv_shows_table.grant_read_write_data(delete_tv_show_data_lambda)



        #STEP FUNCTION FOR TRANSCODING

        split_resolutions_lambda = _lambda.Function(
            self, "SplitResolutionsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="splitResolutions/split_resolutions.handler",
            code=_lambda.Code.from_asset("lambda/multimedia"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )

        resize_video_lambda = _lambda.Function(self, "ResizeVideoFunction",
                                               runtime=_lambda.Runtime.PYTHON_3_12,
                                               handler="resizeVideo/resize_video.resize",
                                               code=_lambda.Code.from_asset("lambda/multimedia"),
                                               memory_size=512,
                                               timeout=Duration.seconds(60),
                                               environment=lambda_env,
                                               layers=[ _lambda.LayerVersion.from_layer_version_arn(self, 'ffmpeg',
                                                                                                   'arn:aws:lambda:eu-central-1:590183980405:layer:ffmpeg:1'),
                                                       ]

                                               )

        # Step Function Tasks
        split_task = tasks.LambdaInvoke(
            self, "SplitResolutions",
            lambda_function=split_resolutions_lambda,
            output_path="$.Payload"
        )

        transcode_720p_task = tasks.LambdaInvoke(
            self, "TranscodeAndUpload720p",
            lambda_function=resize_video_lambda,
            payload=sfn.TaskInput.from_object({
                "original_key": sfn.JsonPath.string_at("$.original_key"),
                "target_resolution": 720
            }),
            result_path="$.transcode720p"
        ).add_retry(
            max_attempts=3,
            interval=Duration.seconds(5)
        )

        transcode_480p_task = tasks.LambdaInvoke(
            self, "TranscodeAndUpload480p",
            lambda_function=resize_video_lambda,
            payload=sfn.TaskInput.from_object({
                "original_key": sfn.JsonPath.string_at("$.original_key"),
                "target_resolution": 480
            }),
            result_path="$.transcode480p"
        ).add_retry(
            max_attempts=3,
            interval=Duration.seconds(5)
        )

        transcode_360p_task = tasks.LambdaInvoke(
            self, "TranscodeAndUpload360p",
            lambda_function=resize_video_lambda,
            payload=sfn.TaskInput.from_object({
                "original_key": sfn.JsonPath.string_at("$.original_key"),
                "target_resolution": 360
            }),
            result_path="$.transcode360p"
        ).add_retry(
            max_attempts=3,
            interval=Duration.seconds(5)
        )


        # Parallel State for Transcoding
        parallel_transcode = sfn.Parallel(self, "ParallelTranscode")
        parallel_transcode.branch(transcode_720p_task)
        parallel_transcode.branch(transcode_480p_task)
        parallel_transcode.branch(transcode_360p_task)

        # State Machine Definition
        definition = split_task.next(parallel_transcode)

        state_machine = sfn.StateMachine(
            self, "VideoProcessingStateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            timeout=Duration.minutes(10)
        )

        # Lambda to start the Step Function execution
        start_step_function_lambda = _lambda.Function(
            self, "StartSplittingResolutionsFunctionExecution",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="startSplittingResolutions/start_splitting_resolutions.handler",
            code=_lambda.Code.from_asset("lambda/multimedia"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment={
                "STATE_MACHINE_ARN": state_machine.state_machine_arn
            }
        )

        state_machine.grant_start_execution(start_step_function_lambda)

        transcode_resource = video_resource.add_resource("transcode")
        transcode_resource.add_method("PUT", apigateway.LambdaIntegration(start_step_function_lambda),
                                  authorization_type=apigateway.AuthorizationType.COGNITO,
                                  authorizer=authorizer,
                                  )

        s3_bucket.grant_read_write(split_resolutions_lambda)
        s3_bucket.grant_read_write(resize_video_lambda)