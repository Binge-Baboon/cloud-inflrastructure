from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    Duration,
    Stack,
    CfnOutput,
    Aws,
    RemovalPolicy,
)
from constructs import Construct

from cdk_init.cdk_init_stack import BingeBaboonServiceStack


class TvShowsServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer


        # Create DynamoDB Table
        self.tv_shows_table = dynamodb.Table(self, "TvShowsTable",
            table_name="TvShows",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY,
            stream = dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )


        bucket_name = "binge-baboon"
        s3_bucket = s3.Bucket.from_bucket_name(self, "BingeBaboonBucket", bucket_name)

        lambda_env = {
            "TABLE_NAME": self.tv_shows_table.table_name,
            "BUCKET_NAME": bucket_name
        }

        create_tv_show_lambda = _lambda.Function(self, "CreateTvShowFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createTvShow/create_tv_show.create",
            code=_lambda.Code.from_asset("lambda/tvShows"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        get_tv_shows_lambda = _lambda.Function(self, "GetTvShowsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getTvShows/get_tv_shows.get_all",
            code=_lambda.Code.from_asset("lambda/tvShows"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        get_tv_show_lambda = _lambda.Function(self, "GetTvShowFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getTvShow/get_tv_show.get_one",
            code=_lambda.Code.from_asset("lambda/tvShows"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        update_tv_show_lambda = _lambda.Function(self, "UpdateTvShowFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="updateTvShow/update_tv_show.update",
            code=_lambda.Code.from_asset("lambda/tvShows"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        delete_tv_show_lambda = _lambda.Function(self, "DeleteTvShowFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="deleteTvShow/delete_tv_show.delete",
            code=_lambda.Code.from_asset("lambda/tvShows"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )

        search_tv_shows_lambda = _lambda.Function(self, "SearchMoviesFunction",
                                                runtime=_lambda.Runtime.PYTHON_3_12,
                                                handler="searchTvShows/search_tv_shows.search",
                                                code=_lambda.Code.from_asset("lambda/tvShows"),
                                                memory_size=128,
                                                timeout=Duration.seconds(10),
                                                environment=lambda_env
                                                )

        # Grant Lambda functions permissions to interact with DynamoDB and S3
        self.tv_shows_table.grant_read_write_data(create_tv_show_lambda)
        self.tv_shows_table.grant_read_write_data(get_tv_shows_lambda)
        self.tv_shows_table.grant_read_write_data(get_tv_show_lambda)
        self.tv_shows_table.grant_read_write_data(update_tv_show_lambda)
        self.tv_shows_table.grant_read_write_data(delete_tv_show_lambda)
        self.tv_shows_table.grant_read_write_data(search_tv_shows_lambda)


        # Create API Gateway resources and methods
        tvShows_resource = api.root.add_resource("tv-shows")

        tvShows_resource.add_method("POST", apigateway.LambdaIntegration(create_tv_show_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        tvShows_resource.add_method("GET", apigateway.LambdaIntegration(get_tv_shows_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )



        tv_show_resource = tvShows_resource.add_resource("{id}")

        tv_show_resource.add_method("GET", apigateway.LambdaIntegration(get_tv_show_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        tv_show_resource.add_method("PUT", apigateway.LambdaIntegration(update_tv_show_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        tv_show_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_tv_show_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )

        search_resource = tvShows_resource.add_resource("search")
        search_resource.add_method("PUT", apigateway.LambdaIntegration(search_tv_shows_lambda),
                                   authorization_type=apigateway.AuthorizationType.COGNITO,
                                   authorizer=authorizer,
                                   )