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


class UsersServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer


        # Create DynamoDB Table
        users_table = dynamodb.Table(self, "UsersTable",
            table_name="Users",
            partition_key=dynamodb.Attribute(name="username", type=dynamodb.AttributeType.STRING),
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

        # Grant Lambda functions permissions to interact with DynamoDB and S3
        users_table.grant_read_write_data(create_user_lambda)
        users_table.grant_read_write_data(get_users_lambda)
        users_table.grant_read_write_data(get_user_lambda)
        users_table.grant_read_write_data(update_user_lambda)
        users_table.grant_read_write_data(delete_user_lambda)

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
        user_resource = users_resource.add_resource("{username}")

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