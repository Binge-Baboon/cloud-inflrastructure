from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct

class BingeBaboonServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Cognito User Pool
        self.user_pool = cognito.UserPool(self, "CognitoUserPool",
            user_pool_name="binge-baboon-users2",
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            sign_in_aliases=cognito.SignInAliases(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            mfa=cognito.Mfa.OFF,
            email=cognito.UserPoolEmail.with_cognito(),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Cognito User Pool Client
        self.user_pool_client = cognito.UserPoolClient(self, "CognitoUserPoolClient",
            user_pool=self.user_pool,
            auth_flows=cognito.AuthFlow(
                user_srp=True,
                # allow_refresh_token=True
            )
        )

        # Define the Lambda function
        hello_lambda = _lambda.Function(self, "HelloHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.hello",
            code=_lambda.Code.from_asset("lambda"),
            memory_size=128,
            timeout=Duration.seconds(10)
        )

        # Create API Gateway REST API
        self.api = apigateway.RestApi(self, "ApiGatewayRestApi",
            rest_api_name="BingeBaboonService",
            default_cors_preflight_options={
                "allow_origins": apigateway.Cors.ALL_ORIGINS,
                "allow_headers": ["Authorization"]
            }
        )

        # Integrate Lambda with API Gateway
        hello_integration = apigateway.LambdaIntegration(hello_lambda)

        self.authorizer = apigateway.CognitoUserPoolsAuthorizer(self, "ApiGatewayCognitoAuthorizer",
                                                           cognito_user_pools=[self.user_pool]
                                                           )

        # Add a resource and method to the API
        hello_resource = self.api.root.add_resource("hello")
        hello_resource.add_method("GET", hello_integration,
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=self.authorizer
        )

        # Output User Pool details
        CfnOutput(self, "CognitoUserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "CognitoUserPoolClientId", value=self.user_pool_client.user_pool_client_id)
        CfnOutput(self, "ApiGatewayRestApiId", value=self.api.rest_api_id)
        CfnOutput(self, "ApiGatewayRestApiRootResourceId", value=self.api.root.resource_id)

