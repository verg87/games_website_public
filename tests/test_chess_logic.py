from django.test import TestCase
from core.base_board import base
from core.chess_classes.chess_logic import ChessLogic
from core.chess_classes.chess_pieces import Pawn, Rook, King


class ChessLogicTests(TestCase):

    def setUp(self):
        self.chess_logic = ChessLogic()

    def test_handle_check(self) -> None:
        """Test ChessLogic's handle_check method"""

        board = base()
        board_v2 = base()

        board['e1'] = 'WK'
        board['f3'] = 'BH' 
        board['f7'] = 'BR'
        board['g2'] = 'WP'
        board['a2'] = 'WP'

        board_v2['e8'] = 'BK'
        board_v2['h7'] = 'BR'
        board_v2['e1'] = 'WQ'

        white_pawn = Pawn('white', board)
        black_rook = Rook('black', board)

        black_rook_h7 = Rook('black', board_v2)

        valid_moves = {
            'capture_enemy_piece': ('g2', 'f3', white_pawn),
            'block_check': ('h7', 'e7',  black_rook_h7),
        }

        invalid_moves = {
            'pawn_move_when_king_in_check': ('a2', 'a4', white_pawn),
            'capture_enemy_piece_with_enemy_rook': ('f7', 'f3', black_rook),
        }

        for value in valid_moves.values():
            move = self.chess_logic.handle_check(*value)

            self.assertIsNone(move)

        for value in invalid_moves.values():
            move = self.chess_logic.handle_check(*value)

            self.assertEqual(move['processed_cell'], value[1])

            self.assertFalse(move['move_valid'])
            self.assertFalse(move['checkmate'])

            self.assertTrue(move['check'])

    def test_is_checkmate(self) -> None:
        """Test ChessLogic's is_checkmate method"""

        board = base()

        board['e1'] = 'WK'
        board['e7'] = 'BR'

        # Just check
        self.assertFalse(self.chess_logic.is_checkmate('e7', board, 'WK'))

        board['f7'] = board['d7'] = 'BR'

        self.assertTrue(self.chess_logic.is_checkmate('e7', board, 'WK'))

        board['h2'] = 'WR'

        # The king can block the check
        self.assertFalse(self.chess_logic.is_checkmate('e7', board, 'WK'))

        board['e7'] = 'empty'

        # King is not under check and there's no king in the board
        self.assertFalse(self.chess_logic.is_checkmate('f7', board, 'WK'))
        self.assertFalse(self.chess_logic.is_checkmate('f7', board, 'BK'))

    def test_handle_promotion_choice(self) -> None:
        """Test ChessLogic's handle_promotion_choice method"""

        board = base()

        board['e1'] = 'WP'

        # white pawn on e1 is not promotion
        self.assertIsNone(self.chess_logic.handle_promotion_choice(board))

        board['d1'] = 'BP'

        # black pawn on d1 is promotion
        self.assertEqual(type(self.chess_logic.handle_promotion_choice(board)), str)

        board['d1'] = board['e1'] = 'empty'
        board['f8'] = 'BP'

        self.assertIsNone(self.chess_logic.handle_promotion_choice(board))

        board['d8'] = 'WP'

        self.assertEqual(type(self.chess_logic.handle_promotion_choice(board)), str)

    def test_handle_move(self) -> None:
        """Test ChessLogic's handle_move method"""

        King.last_checked_king = ''
        King.last_moved_piece = ''
        King.enemy_check_position = ''

        board = base()

        invalid_moves = {
            'invalid_target_and_current_positions': [('1', 'a', 'WQ')],
            'empty_arguments': [('1', '', None)],
            'invalid_piece_name': [('a1', 'h8', 'WE')],
            'invalid_pawn_move': [('e2', 'd4', 'WP')],
            'move_piece_when_pawn_promotion': [('e2', 'e4', 'WP'), ('a1', 'BP')],
            'move_piece_when_in_check': [('a7', 'a5', 'BP'), ('e1', 'WK', 'e4', 'BQ')],
        }

        for value in invalid_moves.values():

            if len(value) == 2:
                board[value[1][0]] = value[1][1]

                if len(value[1]) == 4:
                    board[value[1][2]] = value[1][3]

            self.assertEqual(self.chess_logic.handle_move(*value[0], board)['move_valid'], False)

            board = base()

            King.last_checked_king = ''
            King.last_moved_piece = ''
            King.enemy_check_position = ''

        self.assertEqual(self.chess_logic.handle_move('e2', 'e4', 'WP', board)['move_valid'], True)
  