from django.urls import re_path
from .consumers import ChessConsumer

websocket_urlpatterns = [
    re_path('ws/chess/', ChessConsumer.as_asgi()),
]