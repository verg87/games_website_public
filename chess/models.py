from django.db import models
from ast import literal_eval
from core.generic_models.time_stamp_model import TimeStampedModel
from core.base_board import base
from core.chess_classes.chess_pieces import Piece, Pawn, King, Rook
from core.chess_classes.chess_utils import update_king_move_count, update_rook_move_count
from core.chess_classes.chess_logic import ChessLogic


class Board(TimeStampedModel):

    # Can't just set default to mutable dict, so use a callable
    grid = models.TextField(default=base)
    letters = ["a", "b", "c", "d", "e", "f", "g", "h"]

    def __str__(self) -> str:
        return f"Chess board: {self.id}"

    def get_object(self):
        return Board.objects.last()

    def update_board(
        self,
        last_obj,
        old_cell: str,
        new_cell: str,
        piece: str,
        castle: bool,
        promoted_to: str = None,
    ) -> None:
        if not old_cell and not new_cell and not piece or old_cell == new_cell:
            return last_obj

        update_rook_move_count(old_cell, piece)
        update_king_move_count(piece)

        Piece.last_moved_piece = (piece, old_cell, new_cell)
        Pawn.is_en_passant = False

        board = literal_eval(last_obj.grid) if type(last_obj.grid) == str else {}

        board[old_cell] = "empty"

        # ChessLogic.last_side_to_move = piece[0]

        if castle:
            # Short castle
            if self.letters.index(old_cell[0]) < self.letters.index(new_cell[0]):

                board["h" + new_cell[1]] = "empty"  # Rook
                board["f" + new_cell[1]] = piece[0] + "R"

                board["g" + new_cell[1]] = piece[0] + "K"

            # Long castle
            elif self.letters.index(old_cell[0]) > self.letters.index(new_cell[0]):
                board["a" + new_cell[1]] = "empty"  # Rook
                board["d" + new_cell[1]] = piece[0] + "R"

                board["c" + new_cell[1]] = piece[0] + "K"
    
            last_obj.grid = board
            last_obj.save()

        elif promoted_to:
            board[new_cell] = promoted_to

            last_obj.grid = board
            last_obj.save()

        else:
            board[new_cell] = piece

            last_obj.grid = board
            last_obj.save()

        return last_obj
    

    def create_game(self, is_checkmate) -> None:
        if is_checkmate:
            Board.objects.create()

    def game_status(self) -> dict:
        last_obj = Board.objects.last()
        default = base()
        current_board = (
            literal_eval(last_obj.grid) if type(last_obj.grid) == str else {}
        )

        if current_board == default:
            return {"code": "initialize", "last_obj": last_obj}
        return {"code": False, "last_obj": last_obj}

    def initialize_board(self) -> None:
        # ? Sometimes this method fires twice when moving piece quickly
        game_status = self.game_status()

        if game_status["code"] == "initialize":
            print("initializing...")
            board = base()

            initial_positions = {
                "a1": "WR",
                "h1": "WR",
                "b1": "WH",
                "g1": "WH",
                "c1": "WB",
                "f1": "WB",
                "d1": "WQ",
                "e1": "WK",
                "a8": "BR",
                "h8": "BR",
                "b8": "BH",
                "g8": "BH",
                "c8": "BB",
                "f8": "BB",
                "d8": "BQ",
                "e8": "BK",
            }

            board.update(initial_positions)
            board.update({f"{char}2": "WP" for char in "abcdefgh"})  # White pawns
            board.update({f"{char}7": "BP" for char in "abcdefgh"})  # Black pawns

            # self.grid = board will update the instance's grid not the actual database's grid
            game_status["last_obj"].grid = board

            game_status["last_obj"].save()

        return game_status["last_obj"]

    def reset_board(self, last_obj):
        last_obj.grid = base()
        King.black_move_count = King.white_move_count = 0
        Rook.black_left_move_count = Rook.black_right_move_count = 0
        Rook.white_left_move_count = Rook.white_right_move_count = 0
        King.last_checked_king = King.enemy_check_position = ""
        Piece.last_moved_piece = ()
        Pawn.is_en_passant = False
        # ChessLogic.last_side_to_move = "B"

        last_obj.save()
