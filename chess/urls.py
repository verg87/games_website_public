from django.urls import path
from .views import chess_page

urlpatterns = [
    path('chess/', chess_page, name='chess')
]