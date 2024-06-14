#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_init.cdk_init_stack import BingeBaboonServiceStack
from movie_service.movie_service_stack import MoviesServiceStack
from subscriptions_service.subscriptions_service_stack import SubscriptionsServiceStack
from user_service.user_service_stack import UsersServiceStack
from config import REST_API_ID, REST_API_ROOT_RESOURCE_ID, AUTHORIZER_ID


app = cdk.App()
init_stack = BingeBaboonServiceStack(app, "BingeBaboonServiceStack")
subscriptions_stack = SubscriptionsServiceStack(app, 'SubscriptionServiceStack',
    init_stack= init_stack
)
MoviesServiceStack(app, "MoviesServiceStack",
    init_stack = init_stack,
    subscriptions_stack = subscriptions_stack
)
UsersServiceStack(app, "UserServiceStack",
    init_stack = init_stack
)


app.synth()
