from django.urls import path
from .views import GuessNumView

urlpatterns = [
    path("guess_the_number/", GuessNumView.as_view(), name="comp-guesses-num"),
]