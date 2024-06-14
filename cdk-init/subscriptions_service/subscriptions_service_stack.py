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

class SubscriptionsServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer


        # Create DynamoDB Table
        genres_table = dynamodb.Table(self, "GenresTable",
            table_name="Genres",
            partition_key=dynamodb.Attribute(name="genre", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )

        actors_table = dynamodb.Table(self, "ActorsTable",
            table_name="Actors",
            partition_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )

        directors_table = dynamodb.Table(self, "DirectorsTable",
            table_name="Directors",
            partition_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )



        # Create Lambda functions
        genres_lambda_env = {
            "TABLE_NAME": genres_table.table_name
        }

        actors_lambda_env = {
            "TABLE_NAME": actors_table.table_name
        }

        directors_lambda_env = {
            "TABLE_NAME": directors_table.table_name
        }

        create_genre_lambda = _lambda.Function(self, "CreateGenreFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createGenre/create_genre.create",
            code=_lambda.Code.from_asset("lambda/subscriptions/genres"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=genres_lambda_env
        )

        get_genres_lambda = _lambda.Function(self, "GetGenresFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getGenres/get_genres.get_all",
            code=_lambda.Code.from_asset("lambda/subscriptions/genres"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=genres_lambda_env
        )
        get_genre_lambda = _lambda.Function(self, "GetGenreFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getGenre/get_genre.get_one",
            code=_lambda.Code.from_asset("lambda/subscriptions/genres"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=genres_lambda_env
        )

        delete_genre_lambda = _lambda.Function(self, "DeleteGenreFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="deleteGenre/delete_genre.delete",
            code=_lambda.Code.from_asset("lambda/subscriptions/genres"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=genres_lambda_env
        )

        create_actor_lambda = _lambda.Function(self, "CreateActorFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createActor/create_actor.create",
            code=_lambda.Code.from_asset("lambda/subscriptions/actors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=actors_lambda_env
        )

        get_actors_lambda = _lambda.Function(self, "GetActorsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getActors/get_actors.get_all",
            code=_lambda.Code.from_asset("lambda/subscriptions/actors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=actors_lambda_env
        )
        get_actor_lambda = _lambda.Function(self, "GetActorFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getActor/get_actor.get_one",
            code=_lambda.Code.from_asset("lambda/subscriptions/actors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=actors_lambda_env
        )

        delete_actor_lambda = _lambda.Function(self, "DeleteActorFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="deleteActor/delete_actor.delete",
            code=_lambda.Code.from_asset("lambda/subscriptions/actors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=actors_lambda_env
        )

        create_director_lambda = _lambda.Function(self, "CreateDirectorFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="createDirector/create_director.create",
            code=_lambda.Code.from_asset("lambda/subscriptions/directors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=directors_lambda_env
        )

        get_directors_lambda = _lambda.Function(self, "GetDirectorsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getDirectors/get_directors.get_all",
            code=_lambda.Code.from_asset("lambda/subscriptions/directors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=directors_lambda_env
        )
        get_director_lambda = _lambda.Function(self, "GetDirectorFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="getDirector/get_director.get_one",
            code=_lambda.Code.from_asset("lambda/subscriptions/directors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=directors_lambda_env
        )

        delete_director_lambda = _lambda.Function(self, "DeleteDirectorFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="deleteDirector/delete_director.delete",
            code=_lambda.Code.from_asset("lambda/subscriptions/directors"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=directors_lambda_env
        )


        # Grant Lambda functions permissions to interact with DynamoDB and S3
        genres_table.grant_read_write_data(create_genre_lambda)
        genres_table.grant_read_write_data(get_genres_lambda)
        genres_table.grant_read_write_data(get_genre_lambda)
        genres_table.grant_read_write_data(delete_genre_lambda)

        actors_table.grant_read_write_data(create_actor_lambda)
        actors_table.grant_read_write_data(get_actors_lambda)
        actors_table.grant_read_write_data(get_actor_lambda)
        actors_table.grant_read_write_data(delete_actor_lambda)

        directors_table.grant_read_write_data(create_director_lambda)
        directors_table.grant_read_write_data(get_directors_lambda)
        directors_table.grant_read_write_data(get_director_lambda)
        directors_table.grant_read_write_data(delete_director_lambda)

        # Create API Gateway resources and methods
        genres_resource = api.root.add_resource("genres")

        genres_resource.add_method("POST", apigateway.LambdaIntegration(create_genre_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        genres_resource.add_method("GET", apigateway.LambdaIntegration(get_genres_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        genres_resource =  genres_resource.add_resource("{genre}")

        genres_resource.add_method("GET", apigateway.LambdaIntegration(get_genre_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        genres_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_genre_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )

        actors_resource = api.root.add_resource("actors")

        actors_resource.add_method("POST", apigateway.LambdaIntegration(create_actor_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        actors_resource.add_method("GET", apigateway.LambdaIntegration(get_actors_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        actors_resource = actors_resource.add_resource("{name}")

        actors_resource.add_method("GET", apigateway.LambdaIntegration(get_actor_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        actors_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_actor_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )

        directors_resource = api.root.add_resource("directors")

        directors_resource.add_method("POST", apigateway.LambdaIntegration(create_director_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        directors_resource.add_method("GET", apigateway.LambdaIntegration(get_directors_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        directors_resource = directors_resource.add_resource("{name}")

        directors_resource.add_method("GET", apigateway.LambdaIntegration(get_director_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )
        directors_resource.add_method("DELETE", apigateway.LambdaIntegration(delete_director_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
            # api_key_required=True
        )