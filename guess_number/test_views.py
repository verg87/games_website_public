from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class GuessNumViewTests(TestCase):
    client = Client

    def setUp(self):
        self.path = "/guess_the_number/"
        self.ctx_results = ["bot_guess", "rounds", "accuracy"]
        self.ctx_var = "user_input"

        usr = "testuser"
        psw = "some12psw23"

        User = get_user_model()
        User.objects.create_user(username=usr, password=psw)

        self.client.login(username=usr, password=psw)

    def test_back(self):
        response = self.client.post(self.path, {"back": ""})

        self.assertRedirects(response, reverse("home"))