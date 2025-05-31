from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpResponse
from django.urls import reverse

class TicTacToeTests(TestCase):

    path = "/tic_tac_toe/"
    view_name = "tic-tac-toe"
    template_name = "tic_tac_toe.html"

    username = "somedude"
    password = "some12psw23"

    context_var = "cell_index"

    def _validate_player_move(self, move: HttpResponse, next_player: str) -> None:
        """Checks if user move is handled properly"""

        self.assertEqual(move.status_code, 200, "Response status for Player should be 200 OK")
        self.assertIn("current_player", self.client.session, "current_player should be in session")
        self.assertEqual(self.client.session["current_player"], next_player, "Turn should switch to the other Player")

    def _play_tic_tac_toe(self, player_o_moves: list, player_x_moves: list) -> None:
        """Plays a game of Tic Tac Toe"""

        for o_move, x_move in zip(player_o_moves, player_x_moves):
            response_o = self.client.post(self.path, {self.context_var: o_move})
            self._validate_player_move(response_o, "X")

            response_x = self.client.post(self.path, {self.context_var: x_move})
            self._validate_player_move(response_x, "O")

    def setUp(self) -> None:
        User = get_user_model()
        User.objects.create_user(username=self.username, password=self.password)

        self.client.login(username=self.username, password=self.password)

    def test_not_logged_in_user(self) -> None:
        """Test that not logged in users can't access the game"""

        self.client.logout()
        
        response = self.client.get(reverse(self.view_name))

        self.assertEqual(response.status_code, 302)

    def test_path(self) -> None:
        """Test status code, template and view_name"""

        response = self.client.get(reverse(self.view_name))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_game_board_is_rendered(self) -> None:
        """Test if game board is rendered correctly"""

        response = self.client.get(self.path)

        self.assertIn('name="cell_index"', response.content.decode())

    def test_game_board_updates_after_click(self) -> None:
        """Test if game board updates after a click"""

        response = self.client.post(self.path, {self.context_var: 0})

        self.assertEqual(response.context['cell'], "X")

    def test_player_win_via_diagonal(self) -> None:
        """Test if a player wins when they complete a diagonal."""

        x_moves = [4, 8]
        o_moves = [1, 2]
 
        self.client.post(self.path, {self.context_var: 0})
        self._play_tic_tac_toe(o_moves, x_moves)

        self.assertEqual(self.client.session["winner"], "X")

    def test_player_win_via_row(self) -> None:
        """Test if a player wins when they complete a row."""

        x_moves = [4, 7, 8]
        o_moves = [0, 1, 2]

        self.client.post(self.path, {self.context_var: 3})
        self._play_tic_tac_toe(o_moves, x_moves)

        self.assertEqual(self.client.session["winner"], "O")

    def test_player_win_via_column(self) -> None:
        """Test if a player wins when they complete a row."""

        x_moves = [2, 8, 1]
        o_moves = [0, 3, 6]

        self.client.post(self.path, {self.context_var: 4})
        self._play_tic_tac_toe(o_moves, x_moves)

        self.assertEqual(self.client.session["winner"], "O")

    def test_stalemate(self) -> None:
        """Test stalemate"""

        x_moves = [4, 5, 7, 2]
        o_moves = [1, 8, 3, 6]

        self.client.post(self.path, {self.context_var: 0})
        self._play_tic_tac_toe(o_moves, x_moves)

        self.assertEqual(self.client.session["winner"], "Stalemate")
        response = self.client.post(self.path, {"reset_button": ""})

        self.assertIn('value="0"', response.content.decode())

    def test_place_is_taken_error(self):
        """Test error handling"""

        x_moves = [0, 4]
        o_moves = [3, 4]

        self.client.post(self.path, {self.context_var: x_moves[0]})
        self.client.post(self.path, {self.context_var: o_moves[0]})
        self.client.post(self.path, {self.context_var: x_moves[1]})

        response = self.client.post(self.path, {self.context_var: o_moves[1]})
        
        self.assertTrue(response.context['error_message'])
        