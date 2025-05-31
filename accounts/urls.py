from django.urls import path
from .views import Login, Signup

urlpatterns = [
    path("login/", Login.as_view(), name="login"),
    path("sign_up/", Signup.as_view(), name="sign-up"),
]