from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth import get_user_model

client = Client()

class GuessNumUrlsTests(TestCase):
    def setUp(self):
        self.path = "/guess_the_number/"
        self.view_name = "comp-guesses-num"
        self.template = "guess_number.html"

        self.username = "testuser"
        self.password = "some12psw23"

        User = get_user_model()
        User.objects.create_user(username=self.username, password=self.password)

        client.login(username=self.username, password=self.password)

    def test_not_logged_in_user(self):
        client.logout()

        response = client.get(self.path)

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user(self):
        response_path = client.get(self.path)
        response_view_name = client.post(reverse(self.view_name))

        self.assertEqual(response_path.status_code, 200)
        self.assertEqual(response_view_name.status_code, 200)

        self.assertTemplateUsed(response_view_name, self.template)