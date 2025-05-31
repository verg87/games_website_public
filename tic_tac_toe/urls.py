from django.urls import path
from .views import TicTacToeGame

urlpatterns = [
    path("tic_tac_toe/", TicTacToeGame.as_view(), name="tic-tac-toe")
]