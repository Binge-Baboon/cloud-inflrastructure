from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    Duration,
    Stack,
    CfnOutput,
    Aws,
    RemovalPolicy
)
from constructs import Construct

from cdk_init.cdk_init_stack import BingeBaboonServiceStack
from movie_service.movie_service_stack import MoviesServiceStack
from tvShowService.tv_show_service_stack import TvShowsServiceStack

class UsersServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, movies_stack: MoviesServiceStack, tv_shows_stack: TvShowsServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer


        # Create DynamoDB Table
        users_table = dynamodb.Table(self, "UsersTable",
            table_name="Users",
            partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )



        # Create Lambda functions
        lambda_env = {
            "TABLE_NAME": users_table.table_name
        }

        create_user_lambda = _lambda.Function(self, "CreateUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createUser/create_user.create",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        get_users_lambda = _lambda.Function(self, "GetUsersFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getUsers/get_users.get_all",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        get_user_lambda = _lambda.Function(self, "GetUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getUser/get_user.get_one",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        update_user_lambda = _lambda.Function(self, "UpdateUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="updateUser/update_user.update",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        delete_user_lambda = _lambda.Function(self, "DeleteUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="deleteUser/delete_user.delete",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )

        add_watched_lambda = _lambda.Function(self, "AddWatchedFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="addWatched/add_watched.add",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )

        add_downloaded_lambda = _lambda.Function(self, "AddDownloadedFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="addDownloaded/add_downloaded.add",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )

        generate_feed_lambda = _lambda.Function(self, "GenerateFeedFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="generateFeed/generate_feed.generate",
            code=_lambda.Code.from_asset("lambda/users"),
            memory_size=128,
            timeout=Duration.seconds(30),
            environment=lambda_env
        )

        # Grant Lambda functions permissions to interact with DynamoDB and S3
        users_table.grant_read_write_data(create_user_lambda)
        users_table.grant_read_write_data(get_users_lambda)
        users_table.grant_read_write_data(get_user_lambda)
        users_table.grant_read_write_data(update_user_lambda)
        users_table.grant_read_write_data(delete_user_lambda)
        users_table.grant_read_write_data(add_watched_lambda)
        users_table.grant_read_write_data(add_downloaded_lambda)
        users_table.grant_read_write_data(generate_feed_lambda)
        movies_stack.movies_table.grant_read_write_data(generate_feed_lambda)
        tv_shows_stack.tv_shows_table.grant_read_write_data(generate_feed_lambda)


        # Create API Gateway resources and methods
        users_resource = api.root.add_resource("users")

        users_resource.add_method("POST", apigateway.LambdaIntegration(create_user_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        users_resource.add_method("GET", apigateway.LambdaIntegration(get_users_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        user_resource = users_resource.add_resource("{email}")

        user_resource.add_method("GET", apigateway.LambdaIntegration(get_user_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        user_resource.add_method("PUT", apigateway.LambdaIntegration(update_user_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        user_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_user_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )

        user_resource_watched = users_resource.add_resource("watched")

        user_resource_watched.add_method("PUT", apigateway.LambdaIntegration(add_watched_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        user_resource_watched = users_resource.add_resource("downloaded")

        user_resource_watched.add_method("PUT", apigateway.LambdaIntegration(add_downloaded_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        user_resource_feed = users_resource.add_resource("feed")
        user_resource_feed = user_resource_feed.add_resource("{user}")

        user_resource_feed.add_method("GET", apigateway.LambdaIntegration(generate_feed_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )