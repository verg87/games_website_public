from django.test import TestCase
from core.chess_classes.chess_pieces import King, Rook
from core.chess_classes.chess_utils import (
    get_path_between_positions,
    update_king_move_count,
    update_rook_move_count,
)

class ChessUtilsTests(TestCase):

    def test_get_path_between_positions(self) -> None:
        """
        Test if the get_path_between_positions returns the path 
        from the piece that checked the king (inclusive) to that king
        """

        moves = {
            ('a1', 'a8'): ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7'], # rook or queen
            ('a1', 'h8'): ['a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7'], # bishop or queen
            ('g1', 'f3'): ['g1'], # vertical horse move
            ('g1', 'e2'): ['g1'], # horizontal horse move
            ('e4', 'd5'): ['e4'], # pawn
        }

        for key, value in moves.items():
            path = get_path_between_positions(*key)

            self.assertEqual(path, value)

    def test_update_rook_move_count(self) -> None:
        """Test if the rook move count increases"""

        corners = ['a1', 'h1', 'a8', 'h8']

        Rook.black_left_move_count = 0
        Rook.white_left_move_count = 0
        Rook.black_right_move_count = 0
        Rook.white_right_move_count = 0
        
        for corner in corners:
            update_rook_move_count(corner, 'WR')

        # test invalid piece argument doesn't affect the move count
        update_rook_move_count(corners[3], "WK")

        self.assertEqual(Rook.white_left_move_count, 1)
        self.assertEqual(Rook.white_right_move_count, 1)
        self.assertEqual(Rook.black_left_move_count, 1)
        self.assertEqual(Rook.black_right_move_count, 1)

    def test_update_king_move_count(self) -> None:
        """Test if the king move count increases"""

        King.white_move_count = 0
        King.black_move_count = 0

        update_king_move_count('WK')
        update_king_move_count('BK')

        # test invalid piece argument doesn't affect the move count
        update_king_move_count('WQ')

        self.assertEqual(King.white_move_count, 1)
        self.assertEqual(King.black_move_count, 1)