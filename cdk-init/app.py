#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_init.cdk_init_stack import BingeBaboonServiceStack
from movie_service.movie_service_stack import MoviesServiceStack
from tvShowService.tv_show_service_stack import TvShowsServiceStack
from subscriptions_service.subscriptions_service_stack import SubscriptionsServiceStack
from user_service.user_service_stack import UsersServiceStack
from multimedia_stack.multimedia_stack import MultimediaServiceStack
from notification_service.notification_service_stack import NotificationServiceStack
from config import REST_API_ID, REST_API_ROOT_RESOURCE_ID, AUTHORIZER_ID
from rating_service.rating_service_stack import RatingServiceStack


app = cdk.App()
init_stack = BingeBaboonServiceStack(app, "BingeBaboonServiceStack")
movies_stack = MoviesServiceStack(app, "MoviesServiceStack",
    init_stack = init_stack,
)
tv_shows_stack = TvShowsServiceStack(app, "TvShowsServiceStack",
    init_stack = init_stack,
)
subscriptions_stack = SubscriptionsServiceStack(app, 'SubscriptionServiceStack',
    init_stack= init_stack,
    movies_stack= movies_stack,
    tv_shows_stack = tv_shows_stack
)
UsersServiceStack(app, "UserServiceStack",
    init_stack = init_stack,
    movies_stack=movies_stack,
    tv_shows_stack=tv_shows_stack
)
MultimediaServiceStack(app, "MultimediaServiceStack",
    init_stack = init_stack,
    movies_stack = movies_stack,
    tv_shows_stack = tv_shows_stack
                       )
notifications_stack = NotificationServiceStack(app, "NotificationServiceStack",
    init_stack = init_stack,
    movies_stack = movies_stack,
    tv_shows_stack = tv_shows_stack
)
rating_service_stack = RatingServiceStack(app, "RatingServiceStack",
    init_stack = init_stack,
    movie_service_stack = movies_stack,
    tv_show_service_stack = tv_shows_stack
                   )

app.synth()