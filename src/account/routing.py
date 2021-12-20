from django.urls import path

from account.consumers.messages import MessagesConsumer
from account.consumers.posts import PostsConsumer
from account.consumers.notifications import NotificationsConsumer


ws_urlpatterns = [
    path('ws/messages/<profile_id>', MessagesConsumer.as_asgi()),
    path('ws/posts/', PostsConsumer.as_asgi()),
    path('ws/notifications/', NotificationsConsumer.as_asgi()),
]
