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
from movie_service.movie_service_stack import MoviesServiceStack
from tvShowService.tv_show_service_stack import TvShowsServiceStack


class RatingServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, movie_service_stack: MoviesServiceStack, tv_show_service_stack: TvShowsServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer

        # Define environment variables
        lambda_env_movies = {
            "TABLE_NAME": movie_service_stack.movies_table.table_name
        }
        lambda_env_tv_shows = {
            "TABLE_NAME": tv_show_service_stack.tv_shows_table.table_name
        }

        # Create Lambda functions for movie ratings
        create_movie_rating_lambda = _lambda.Function(self, "CreateMovieRatingFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createMovieRating.create_movie_rating.add_or_update_rating",
            code=_lambda.Code.from_asset("lambda/ratings"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env_movies
        )

        remove_movie_rating_lambda = _lambda.Function(self, "RemoveMovieRatingFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="removeMovieRating.remove_movie_rating.remove_rating",
            code=_lambda.Code.from_asset("lambda/ratings"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env_movies
        )

        # Create Lambda functions for TV show ratings
        create_tv_show_rating_lambda = _lambda.Function(self, "CreateTvShowRatingFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createTvShowRating.create_tv_show_rating.add_or_update_tv_show_rating",
            code=_lambda.Code.from_asset("lambda/ratings"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env_tv_shows
        )

        remove_tv_show_rating_lambda = _lambda.Function(self, "RemoveTvShowRatingFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="removeTvShowRating.remove_tv_show_rating.remove_tv_show_rating",
            code=_lambda.Code.from_asset("lambda/ratings"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env_tv_shows
        )

        # Grant Lambda functions permissions to interact with DynamoDB
        movie_service_stack.movies_table.grant_read_write_data(create_movie_rating_lambda)
        movie_service_stack.movies_table.grant_read_write_data(remove_movie_rating_lambda)

        tv_show_service_stack.tv_shows_table.grant_read_write_data(create_tv_show_rating_lambda)
        tv_show_service_stack.tv_shows_table.grant_read_write_data(remove_tv_show_rating_lambda)

        # Create API Gateway resources and methods for movies
        movie_ratings_resource = api.root.add_resource("movie-ratings")

        movie_ratings_resource.add_method("POST", apigateway.LambdaIntegration(create_movie_rating_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        movie_ratings_resource.add_method("DELETE", apigateway.LambdaIntegration(remove_movie_rating_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        # Create API Gateway resources and methods for TV shows
        tv_show_ratings_resource = api.root.add_resource("tv-show-ratings")

        tv_show_ratings_resource.add_method("POST", apigateway.LambdaIntegration(create_tv_show_rating_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        tv_show_ratings_resource.add_method("DELETE", apigateway.LambdaIntegration(remove_tv_show_rating_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )