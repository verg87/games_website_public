from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from .forms import CustomUser
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.shortcuts import render

# Create your views here.

class Login(LoginView):
    template_name = "registration/login.html"

class Signup(CreateView):
    form_class = CustomUser
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"