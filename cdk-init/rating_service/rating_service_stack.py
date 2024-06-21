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

from cdk_init.cdk_init_stack import BingeBaboonServiceStack
from constructs import Construct
from movie_service.movie_service_stack import MoviesServiceStack


class RatingServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, movie_service_stack: MoviesServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer




        # Create Lambda functions
        lambda_env = {
            "TABLE_NAME": movie_service_stack.movies_table.table_name
        }

        create_rating_lambda = _lambda.Function(self, "CreateMovieRatingFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createMovieRating.create_movie_rating.add_or_update_rating",
            code=_lambda.Code.from_asset("lambda/ratings"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )


        # Grant Lambda functions permissions to interact with DynamoDB and S3
        movie_service_stack.movies_table.grant_read_write_data(create_rating_lambda)

        # Create API Gateway resources and methods
        movie_ratings_resource = api.root.add_resource("movie-ratings")

        movie_ratings_resource.add_method("POST", apigateway.LambdaIntegration(create_rating_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )

        rating_resource = movie_ratings_resource.add_resource("{username}")

