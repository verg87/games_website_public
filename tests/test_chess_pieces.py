from django.test import TestCase
from core.base_board import base
from core.chess_classes.chess_utils import (
    update_king_move_count,
    update_rook_move_count,
)
from core.chess_classes.chess_pieces import (
    Piece,
    Rook,
    Pawn,
    Horse,
    Bishop,
    Queen,
    King,
)


class PieceTests(TestCase):

    def test_piece_class(self) -> None:
        """Test if __init__ methods of Piece class work"""

        name = "Pawn"
        weight = 1
        side, enemy_side = "white", "black"

        white_pawn = Piece(name, weight, side, base())

        self.assertEqual(white_pawn.name, name)
        self.assertEqual(white_pawn.weight, weight)
        self.assertEqual(white_pawn.side, side)
        self.assertEqual(white_pawn.grid, base())
        self.assertEqual(white_pawn.enemy_side, enemy_side)

    def test_piece_class_str(self) -> None:
        """Test Piece's __str__"""

        white_pawn = Piece("Pawn", 1, "white", base())

        self.assertEqual(str(white_pawn), "Pawn")


class RookTests(TestCase):

    def test_rook_validate_move(self) -> None:
        """Test rook's validate_move method"""

        side = "white"

        board = base()

        board["c3"] = "WP"
        board["b5"] = "BP"
        board["c7"] = "BP"
        board["f5"] = "WH"

        valid_moves = {
            "vertical_move_up": ("a1", "a8"),
            "vertical_move_down": ("h8", "a8"),
            "horizontal_move_right": ("a1", "h1"),
            "horizontal_move_left": ("h8", "a8"),
            "capture_enemy_piece": ("c5", "c7"),
        }

        invalid_moves = {
            "leaving_king_under_check": ("e4", "h4", True),
            "diagnol_move": ("a1", "h8"),
            "piece_in_the_way_ver": ("c5", "c1"),
            "piece_in_the_way_hor": ("c5", "a5"),
            "capture_ally_piece": ("c5", "f5"),
        }

        rook = Rook(side, board)

        for value in valid_moves.values():
            self.assertTrue(rook.validate_move(*value))

        for value in invalid_moves.values():
            self.assertFalse(rook.validate_move(*value))


class PawnClass(TestCase):

    def test_pawn_en_passant(self) -> None:
        """Test if Pawn's en_passant method works fine"""

        valid_moves = {
            "white_en_passant": [("e5", "f6"), ("BP", "f7", "f5")],
            "black_en_passant": [("e4", "f3"), ("WP", "f2", "f4")],
        }

        invalid_moves = {
            ## Description of the move ##    move     ## last moved piece ##
            "white_not_on_a_valid_rank": [("e4", "f6"), ("BP", "f7", "f5")],
            "white_invalid_target_pos": [("e5", "g6"), ("BP", "f7", "f5")],
            "white_en_passant_wrong_direction": [("g5", "h6"), ("BP", "f7", "f5")],
            "white_en_passant_on_far_pawn": [("d5", "f6"), ("BP", "f7", "f5")],
            "white_en_passant_on_black_rook": [("g5", "h6"), ("BR", "h7", "h5")],
            "white_capture_twice_moved_pawn": [("e5", "f6"), ("BP", "f6", "f5")],
            "black_not_on_a_valid_rank": [("d5", "c3"), ("WP", "c2", "c4")],
            "black_invalid_target_pos": [("d4", "b3"), ("WP", "c2", "c4")],
            "black_en_passant_wrong_direction": [("b4", "a3"), ("WP", "c2", "c4")],
            "black_en_passant_on_far_pawn": [("d4", "b3"), ("WP", "c2", "c4")],
            "black_en_passant_on_white_rook": [("b4", "a3"), ("WR", "a2", "a4")],
            "black_capture_twice_moved_pawn": [("d4", "c3"), ("WP", "c3", "c4")],
        }

        white_pawn = Pawn("white", base())
        black_pawn = Pawn("black", base())

        for key, value in valid_moves.items():
            if key.startswith("white"):

                Pawn.last_moved_piece = value[1]

                self.assertTrue(white_pawn.en_passant(*value[0]))
                self.assertTrue(Pawn.is_en_passant)
            else:

                Pawn.last_moved_piece = value[1]

                self.assertTrue(black_pawn.en_passant(*value[0]))
                self.assertTrue(Pawn.is_en_passant)

        for key, value in invalid_moves.items():
            if key.startswith("white"):

                Pawn.last_moved_piece = value[1]
                self.assertFalse(white_pawn.en_passant(*value[0]))
            else:

                Pawn.last_moved_piece = value[1]
                self.assertFalse(black_pawn.en_passant(*value[0]))

    def test_pawn_validate_move_forward(self) -> None:
        """Test if Pawn's validate_move_forward works"""

        board = base()

        board["h4"] = "BP"
        board["g5"] = "WP"

        valid_moves = {
            "white_double_jump": ("a2", "a4"),
            "black_double_jump": ("a7", "a5"),
            "white_move": ("a2", "a3"),
            "black_move": ("a7", "a6"),
        }

        invalid_moves = {
            "white_move_backwards": ("a3", "a2"),
            "white_pawn_out_of_bounds_move": ("a8", "a9"),
            "white_pawn_to_the_occupied_cell": ("h3", "h4"),
            "black_move_backwards": ("a7", "a8"),
            "black_pawn_out_of_bounds_move": ("a1", "a0"),
            "black_pawn_to_the_occupied_cell": ("g7", "g5"),
        }

        white_pawn = Pawn("white", board)
        black_pawn = Pawn("black", board)

        for key, value in valid_moves.items():
            if key.startswith("white"):
                self.assertTrue(white_pawn.validate_move_forward(*value))
            else:
                self.assertTrue(black_pawn.validate_move_forward(*value))

        for key, value in invalid_moves.items():
            if key.startswith("white"):
                self.assertFalse(white_pawn.validate_move_forward(*value))
            else:
                self.assertFalse(black_pawn.validate_move_forward(*value))

    def test_pawn_validate_move_sideways(self) -> None:
        """Test Pawn's validate_move_sideways method"""

        board = base()

        board["g4"] = "BP"
        board["b5"] = "WP"

        valid_moves = {
            "white_capture_enemy_piece": ("f3", "g4"),
            "black_capture_enemy_piece": ("c6", "b5"),
        }

        invalid_moves = {
            "white_no_piece_to_capture": ("f3", "e4"),
            "white_capture_ally_piece": ("a4", "b5"),
            "black_no_piece_to_capture": ("c6", "d5"),
            "black_capture_ally_piece": ("f5", "g4"),
        }

        white_pawn = Pawn("white", board)
        black_pawn = Pawn("black", board)

        for key, value in valid_moves.items():
            if key.startswith("white"):
                self.assertTrue(white_pawn.validate_move_sideways(*value))
            else:
                self.assertTrue(black_pawn.validate_move_sideways(*value))

        for key, value in invalid_moves.items():
            if key.startswith("white"):
                self.assertFalse(white_pawn.validate_move_sideways(*value))
            else:
                self.assertFalse(black_pawn.validate_move_sideways(*value))

    def test_pawn_validate_move(self) -> None:
        """Test Pawn's validate_move"""

        board = base()

        board["g4"] = "BP"

        pawn = Pawn("white", board)

        self.assertTrue(pawn.validate_move("e2", "e4"))
        self.assertTrue(pawn.validate_move("f3", "g4"))

        # test pawn can't move if it's leaving under check it's own king
        self.assertFalse(pawn.validate_move("d2", "d4", True))

        self.assertFalse(pawn.validate_move("e5", "g6"))


class HorseTests(TestCase):

    def test_horse_validate_move(self) -> None:
        """Test Horse's validate move method"""

        board = base()

        board["e2"] = "WK"

        horse = Horse("white", board)

        self.assertTrue(horse.validate_move("g1", "f3"))
        self.assertTrue(horse.validate_move("g8", "e7"))

        self.assertFalse(horse.validate_move("g1", "e2"))
        self.assertFalse(horse.validate_move("g1", "e3"))
        self.assertFalse(horse.validate_move("g1", "f3", True))


class BishopTests(TestCase):

    def test_bishop_validate_move(self) -> None:
        """Test Bishop's validate_move method"""

        board = base()

        board["e2"] = "WK"
        board["f7"] = "BH"

        valid_moves = {
            "top_right_corner": ("a1", "h8"),
            "top_left_corner": ("h1", "a8"),
            "bottom_right_corner": ("a8", "h1"),
            "bottom_left_corner": ("h8", "a1"),
            "capture_enemy_piece": ("d5", "f7"),
        }

        invalid_moves = {
            "move_to_a_blocked_cell": ("f1", "d3"),
            "capture_ally_piece": ("f1", "e2"),
            "leaving_king_under_check": ("d5", "b7", True),
            "move_not_in_the_diagnol_of_the_bishop": ("d5", "h5"),
            "move_out_of_bounds": ("d7", "b9"),
        }

        bishop = Bishop("white", board)

        for value in valid_moves.values():
            self.assertTrue(bishop.validate_move(*value))

        for value in invalid_moves.values():
            self.assertFalse(bishop.validate_move(*value))


class QueenTests(TestCase):

    def test_queen_validate_move(self) -> None:
        """Test Queen validate_move method"""

        queen = Queen("white", base())

        self.assertTrue(queen.validate_move("a1", "h8"))
        self.assertTrue(queen.validate_move("a1", "a8"))

        self.assertFalse(queen.validate_move("e4", "h4", True))
        self.assertFalse(queen.validate_move("e4", "b5"))


class KingTests(TestCase):

    def test_king_is_king_in_check(self) -> None:
        """Test the King's is_king_in_check classmethod"""

        board = base()

        board["e1"] = "WK"
        board["e8"] = "BK"
        board["h5"] = "WQ"

        King.last_checked_king = "BK"

        self.assertTrue(King.is_king_in_check(board, "white", "WK"))

        King.last_checked_king = ""

        self.assertFalse(King.is_king_in_check(board, "white", "WK"))
        self.assertFalse(King.is_king_in_check(board, "white"))

        board["f2"] = "BP"

        self.assertTrue(King.is_king_in_check(board, "white", "WK", True))

        self.assertEqual(King.enemy_check_position, "f2")
        self.assertEqual(King.last_checked_king, "WK")

        King.last_checked_king = ""
        King.enemy_check_position = ""

        self.assertTrue(King.is_king_in_check(board, "black", "BK", True))

        self.assertEqual(King.enemy_check_position, "h5")
        self.assertEqual(King.last_checked_king, "BK")

    def test_king_castle_method(self) -> None:
        """Test the castle method of King's class"""

        King.last_checked_king = ''
        King.enemy_check_position = ''

        initial_board = base()

        initial_board["h1"] = "WR"
        initial_board["a1"] = "WR"
        initial_board["h8"] = "BR"
        initial_board["a8"] = "BR"
        initial_board["e1"] = "WK"
        initial_board["e8"] = "BK"

        valid_moves = {
            "white_short_castle": [("e1", "h1")],
            "white_long_castle": [("e1", "c1")],
            "black_short_castle": [("e8", "g8")],
            "black_long_castle": [("e8", "a8")],
        }

        invalid_moves = {
            "white_king_wrong_target_cell": [("e1", "b1")],
            "black_king_wrong_target_cell": [("e8", "b5")],
            "white_king_moved_before_castle": [("e1", "g1"), "white_king"],
            "black_king_moved_before_castle": [("e8", "g8"), "black_king"],
            "white_king_wrong_starting_cell": [("f1", "h1")],
            "black_king_wrong_starting_cell": [("f8", "h8")],
            "white_short_castle_rook_moved_before": [("e1", "h1"), "rook_h1"],
            "black_short_castle_rook_moved_before": [("e8", "h8"), "rook_h8"],
            "white_short_castle_rook_absent": [("e1", "g1"), ("h1", "empty")],
            "black_short_castle_rook_absent": [("e8", "g8"), ("h8", "empty")],
            "white_f_cell_under_check": [("e1", "h1"), ("c4", "BB")],
            "black_f_cell_under_check": [("e8", "h8"), ("c5", "WB")],
            "white_g_cell_under_check": [("e1", "h1"), ("d4", "BB")],
            "black_g_cell_under_check": [("e8", "h8"), ("d5", "WB")],
            "white_piece_blocks_short_castle": [("e1", "h1"), ("f1", "WB")],
            "black_piece_blocks_short_castle": [("e8", "g8"), ("f8", "BB")],
            "white_long_castle_rook_moved_before": [("e1", "a1"), "rook_a1"],
            "black_long_castle_rook_moved_before": [("e8", "a8"), "rook_a8"],
            "white_long_castle_rook_absent": [("e1", "c1"), ("a1", "empty")],
            "black_long_castle_rook_absent": [("e8", "c8"), ("a8", "empty")],
            "white_d_cell_under_check": [("e1", "a1"), ("g4", "BB")],
            "black_d_cell_under_check": [("e8", "a8"), ("g5", "WB")],
            "white_c_cell_under_check": [("e1", "a1"), ("f4", "BB")],
            "black_c_cell_under_check": [("e8", "a8"), ("f5", "WB")],
            "white_piece_blocks_long_castle": [("e1", "a1"), ("d1", "WQ")],
            "black_piece_blocks_long_castle": [("e8", "c8"), ("c8", "BB")],
        }

        white_king = King("white", initial_board)
        black_king = King("black", initial_board)

        for key, value in valid_moves.items():

            if key.startswith("white"):
                self.assertTrue(white_king.castle(*value[0]))

            else:
                self.assertTrue(black_king.castle(*value[0]))

        for key, value in invalid_moves.items():

            white_king.grid = black_king.grid = initial_board.copy()

            Rook.white_right_move_count = Rook.black_right_move_count = 0
            Rook.white_left_move_count = Rook.black_left_move_count = 0
            King.black_move_count = King.white_move_count = 0

            if key.startswith("white"):

                if len(value) == 1:
                    self.assertFalse(white_king.castle(*value[0]))

                elif type(value[1]) == str:

                    if value[1].startswith("white"):
                        update_king_move_count("WK")
                    else:
                        update_rook_move_count(value[0][1], "WR")

                elif type(value[1]) == tuple:
                    white_king.grid[value[1][0]] = value[1][1]

                self.assertFalse(white_king.castle(*value[0]))

            else:

                if len(value) == 1:
                    self.assertFalse(black_king.castle(*value[0]))

                elif type(value[1]) == str:

                    if value[1].startswith("black"):
                        update_king_move_count("BK")
                    else:
                        update_rook_move_count(value[0][1], "BR")

                elif type(value[1]) == tuple:
                    black_king.grid[value[1][0]] = value[1][1]

                self.assertFalse(black_king.castle(*value[0]))

    def test_king_validate_move(self) -> None:
        """Test king's validate_move method"""

        board = base()

        board["f2"] = "WB"
        board["d2"] = "BH"

        king = King("white", board)

        self.assertTrue(king.validate_move("e1", "e2"))
        self.assertTrue(king.validate_move("e1", "d2"))

        self.assertFalse(king.validate_move("e1", "e2", True))
        self.assertFalse(king.validate_move("e1", "f2"))
