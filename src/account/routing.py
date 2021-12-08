from django.urls import path

from account.consumers.messages import MessagesConsumer


ws_urlpatterns = [
    path('ws/messages/<profile_id>', MessagesConsumer.as_asgi()),
]
