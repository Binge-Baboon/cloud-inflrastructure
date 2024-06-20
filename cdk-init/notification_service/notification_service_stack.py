from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    Duration,
    Stack,
    CfnOutput,
    Aws,
    RemovalPolicy
)
from constructs import Construct

from cdk_init.cdk_init_stack import BingeBaboonServiceStack


class NotificationServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = init_stack.api
        user_pool = init_stack.user_pool
        authorizer = init_stack.authorizer


        # Create Lambda functions
        lambda_env = {

        }


        notify_lambda = _lambda.Function(self, "NotifyFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="notify/notify.handler",
            code=_lambda.Code.from_asset("lambda/notifications"),
            memory_size=128,
            timeout=Duration.seconds(10),
            environment=lambda_env
        )

        subscribe_lambda = _lambda.Function(self, "SubscribeFunction",
                                         runtime=_lambda.Runtime.PYTHON_3_12,
                                         handler="subscribe/subscribe.handler",
                                         code=_lambda.Code.from_asset("lambda/notifications"),
                                         memory_size=128,
                                         timeout=Duration.seconds(10),
                                         environment=lambda_env
                                         )

        unsubscribe_lambda = _lambda.Function(self, "UnsubscribeFunction",
                                            runtime=_lambda.Runtime.PYTHON_3_12,
                                            handler="unsubscribe/unsubscribe.handler",
                                            code=_lambda.Code.from_asset("lambda/notifications"),
                                            memory_size=128,
                                            timeout=Duration.seconds(10),
                                            environment=lambda_env
                                            )


        sns_policy = iam.PolicyStatement(
            actions=[
                "sns:CreateTopic",
                "sns:Subscribe",
                "sns:ListTopics",
                "sns:ListSubscriptionsByTopic",
                "sns:Unsubscribe",
                "sns:Publish"
            ],
            resources=["*"]
        )

        notify_lambda.add_to_role_policy(sns_policy)
        subscribe_lambda.add_to_role_policy(sns_policy)
        unsubscribe_lambda.add_to_role_policy(sns_policy)


        # Create API Gateway resources and methods
        notifications_resource = api.root.add_resource("notifications")
        subscribe_resource = notifications_resource.add_resource("subscribe")
        unsubscribe_resource = notifications_resource.add_resource("unsubscribe")
        notify_resource = notifications_resource.add_resource("notify")


        subscribe_resource.add_method("POST", apigateway.LambdaIntegration(subscribe_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        unsubscribe_resource.add_method("PUT", apigateway.LambdaIntegration(unsubscribe_lambda),
                                      authorization_type=apigateway.AuthorizationType.COGNITO,
                                      authorizer=authorizer,
                                      )

        notify_resource.add_method("POST", apigateway.LambdaIntegration(notify_lambda),
                                      authorization_type=apigateway.AuthorizationType.COGNITO,
                                      authorizer=authorizer,
                                      )
