from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUser(UserCreationForm):

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "date_of_birth", "email")  
