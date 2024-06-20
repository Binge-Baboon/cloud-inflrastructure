from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as lambda_event_sources,
    aws_iam as iam,
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


class NotificationServiceStack(Stack):

    def __init__(self, scope: Construct, id: str, init_stack: BingeBaboonServiceStack, movies_stack: MoviesServiceStack, tv_shows_stack: TvShowsServiceStack, **kwargs) -> None:
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

        handle_notifications_lambda = _lambda.Function(self, "HandleNotificationsFunction",
                                              runtime=_lambda.Runtime.PYTHON_3_12,
                                              handler="handleNotifications/handle_notifications.handler",
                                              code=_lambda.Code.from_asset("lambda/notifications"),
                                              memory_size=128,
                                              timeout=Duration.seconds(10),
                                              environment=lambda_env
                                              )

        list_subscriptions_lambda = _lambda.Function(self, "ListSubscriptionsFunction",
                                                     runtime=_lambda.Runtime.PYTHON_3_12,
                                                     handler="listSubscriptions/list_subscriptions.handler",
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
                "sns:Publish",
                "sns:ListSubscriptions"
            ],
            resources=["*"]
        )

        notify_lambda.add_to_role_policy(sns_policy)
        subscribe_lambda.add_to_role_policy(sns_policy)
        unsubscribe_lambda.add_to_role_policy(sns_policy)
        handle_notifications_lambda.add_to_role_policy(sns_policy)
        list_subscriptions_lambda.add_to_role_policy(sns_policy)


        # Create API Gateway resources and methods
        notifications_resource = api.root.add_resource("notifications")
        subscribe_resource = notifications_resource.add_resource("subscribe")
        unsubscribe_resource = notifications_resource.add_resource("unsubscribe")
        notify_resource = notifications_resource.add_resource("notify")
        list_subscriptions_resource = notifications_resource.add_resource("list-subscriptions")


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
        
        list_subscriptions_resource.add_method("GET", apigateway.LambdaIntegration(list_subscriptions_lambda),
                                               authorization_type=apigateway.AuthorizationType.COGNITO,
                                               authorizer=authorizer,
                                               )

        tv_shows_stack.tv_shows_table.grant_stream_read(handle_notifications_lambda)
        movies_stack.movies_table.grant_stream_read(handle_notifications_lambda)

        handle_notifications_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(tv_shows_stack.tv_shows_table,
                                                   starting_position=_lambda.StartingPosition.LATEST
                                                   ))
        handle_notifications_lambda.add_event_source(lambda_event_sources.DynamoEventSource(movies_stack.movies_table,
                                                                                            starting_position=_lambda.StartingPosition.LATEST
                                                                                            ))
