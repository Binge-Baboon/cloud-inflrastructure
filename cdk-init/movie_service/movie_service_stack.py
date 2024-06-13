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


class MoviesServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer


        # Create DynamoDB Table
        movies_table = dynamodb.Table(self, "MoviesTable",
            table_name="Movies",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )



        # Create Lambda functions
        lambda_env = {
            "TABLE_NAME": movies_table.table_name
        }

        create_movie_lambda = _lambda.Function(self, "CreateMovieFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createMovie/create_movie.create",
            code=_lambda.Code.from_asset("lambda/movies"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        get_movies_lambda = _lambda.Function(self, "GetMoviesFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getMovies/get_movies.get_all",
            code=_lambda.Code.from_asset("lambda/movies"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        get_movie_lambda = _lambda.Function(self, "GetMovieFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getMovie/get_movie.get_one",
            code=_lambda.Code.from_asset("lambda/movies"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        update_movie_lambda = _lambda.Function(self, "UpdateMovieFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="updateMovie/update_movie.update",
            code=_lambda.Code.from_asset("lambda/movies"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )
        delete_movie_lambda = _lambda.Function(self, "DeleteMovieFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="deleteMovie/delete_movie.delete",
            code=_lambda.Code.from_asset("lambda/movies"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )

        # Grant Lambda functions permissions to interact with DynamoDB and S3
        movies_table.grant_read_write_data(create_movie_lambda)
        movies_table.grant_read_write_data(get_movies_lambda)
        movies_table.grant_read_write_data(get_movie_lambda)
        movies_table.grant_read_write_data(update_movie_lambda)
        movies_table.grant_read_write_data(delete_movie_lambda)

        # Create API Gateway resources and methods
        movies_resource = api.root.add_resource("movies")

        movies_resource.add_method("POST", apigateway.LambdaIntegration(create_movie_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        movies_resource.add_method("GET", apigateway.LambdaIntegration(get_movies_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        movie_resource = movies_resource.add_resource("{id}")

        movie_resource.add_method("GET", apigateway.LambdaIntegration(get_movie_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        movie_resource.add_method("PUT", apigateway.LambdaIntegration(update_movie_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        movie_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_movie_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )