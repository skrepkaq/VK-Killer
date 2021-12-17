from django.urls import path

from account.consumers.messages import MessagesConsumer
from account.consumers.posts import PostsConsumer


ws_urlpatterns = [
    path('ws/messages/<profile_id>', MessagesConsumer.as_asgi()),
    path('ws/posts/', PostsConsumer.as_asgi()),
]
