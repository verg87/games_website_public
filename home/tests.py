from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy


class HomePageTests(TestCase):

    path = "/"
    view_name = "home"
    template = "home.html"

    username = "some_username"
    password = "qwaszx34er"

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.login(username=self.username, password=self.password)

    def test_path(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)

    def test_view_name_and_template(self):
        response = self.client.get(reverse(self.view_name))

        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        response = self.client.post(self.path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_page_content_logged_in_user(self):
        response = self.client.get(self.path)
        self.assertContains(response, "<p>Hi %s!</p>" % self.username, html=True)

    def test_page_content_not_logged_in_user(self):
        self.client.logout()

        response = self.client.get(self.path)
        self.assertContains(response, "<p>Please login</p>", html=True)

    def test_links(self):
        response = self.client.get(self.path)

        tic_tac_toe_link = "/tic_tac_toe/"
        tic_tac_toe_text = "Tic tac toe game"

        guess_number_link = "/guess_the_number/"
        guess_number_text = "Computer can you predict you. Click to see how unpredictable you are"

        chess_link = "/chess/"
        chess_text = "Chess"

        self.assertContains(
            response,
            "<li><a href={0}>{1}</a></li>".format(tic_tac_toe_link, tic_tac_toe_text),
            html=True,
        )

        self.assertContains(
            response,
            "<li><a href={0}>{1}</a></li>".format(guess_number_link, guess_number_text),
            html=True,
        )

        self.assertContains(
            response,
            "<li><a href={0}>{1}</a></li>".format(chess_link, chess_text),
            html=True,
        )

    def test_logout(self):
        response = self.client.post(reverse("logout"), follow=True)
    
        self.assertRedirects(response, reverse(self.view_name))
        self.assertContains(response, "<p>Please login</p>", html=True)
