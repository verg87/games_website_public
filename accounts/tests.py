from django.urls import reverse_lazy, reverse
from django.test import TestCase
from .models import User


class SignUpTests(TestCase):

    login_path = "/login/"
    signup_path = "/sign_up/"
    login_view_name = "login"
    signup_view_name = "sign-up"
    login_template = "registration/login.html"
    signup_template = "registration/signup.html"

    def setUp(self):
        self.credentials = {
            "username": "test_user",
            "password1": "some_password1",
            "password2": "some_password1",
            "first_name": "John",
            "last_name": "Johnes",
            "email": "john.johnes@example.com",
            "date_of_birth": "1995-11-13",
        }

    def test_path(self):
        response_login = self.client.get(self.login_path)
        response_sign_up = self.client.get(self.signup_path)

        self.assertEqual(response_login.status_code, 200)
        self.assertEqual(response_sign_up.status_code, 200)

    def test_view_name(self):
        response_login = self.client.get(reverse(self.login_view_name))
        response_sign_up = self.client.get(reverse(self.signup_view_name))

        self.assertTemplateUsed(response_login, self.login_template)
        self.assertTemplateUsed(response_sign_up, self.signup_template)

    def test_signup_form_valid(self):
        sign_up = self.client.post(self.signup_path, self.credentials)

        self.assertRedirects(sign_up, reverse_lazy(self.login_view_name))
        self.assertTrue(User.objects.all().exists())

        self.client.login(
            username=self.credentials["username"],
            password=self.credentials["password1"],
        )

    def test_signup_form_invalid(self):
        invalid_credentials = {k: "" for k in self.credentials.keys()}
        response = self.client.post(self.signup_path, invalid_credentials)

        self.assertTrue(
            all([k not in response.context for k in invalid_credentials.keys()])
        )

        self.assertFalse(User.objects.exists())

        login_attempt = self.client.login(
            username=invalid_credentials["username"],
            password=invalid_credentials["password1"],
        )

        self.assertFalse(login_attempt)
