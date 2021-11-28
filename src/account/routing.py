from django.urls import path

from .consumers import MessagesConsumer


ws_urlpatterns = [
    path('ws/messages/<profile_id>', MessagesConsumer.as_asgi())
]
