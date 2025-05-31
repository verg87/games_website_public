from .chess_pieces import Rook, Pawn, Horse, Bishop, King, Queen
from .chess_utils import get_path_between_positions


class ChessLogic:
    last_side_to_move = "B"
    path = []
    column_labels = ["a", "b", "c", "d", "e", "f", "g", "h"]

    piece_classes = {
        "R": Rook,
        "P": Pawn,
        "K": King,
        "Q": Queen,
        "H": Horse,
        "B": Bishop,
    }

    output = {
        "move_valid": False,
        "checkmate": False,
        "winner": "somebody",
        "check": False,
        "en_passant": False,
    }

    def handle_check(
        self,
        current_pos: str,
        target_pos: str,
        chess_piece,
    ) -> None | dict:
        """
        Checks whether the white or black king is currently under check.
        If so block all moves except the moves of the checked king
        """

        # NOTE Returns None in these cases:
        # NOTE king that is in check moved,
        # NOTE piece that checked king captured by ally
        # NOTE blocking the check

        standart_output = self.output.copy()

        standart_output["processed_cell"] = target_pos

        path = []
        piece_color = chess_piece.side
        piece_name = piece_color[0].upper() + chess_piece.__class__.__name__[0]
        board = chess_piece.grid

        King.is_king_in_check(board, piece_color, "WK", True)
        if not King.last_checked_king:
            King.is_king_in_check(board, piece_color, "BK", True)

        if King.enemy_check_position and King.last_checked_king:
            standart_output["check"] = True
            attacked_piece = board[King.enemy_check_position]

            king_pos = ""
            for cell, piece in board.items():
                if piece == King.last_checked_king:
                    king_pos = cell

            # Calculate the path between the attacked piece and the king
            path = get_path_between_positions(King.enemy_check_position, king_pos)

            # Only pieces of the same color can block a check
            if piece_color[0].upper() == attacked_piece[0]:
                return standart_output

        is_king_checked = (
            King.last_checked_king and piece_name != King.last_checked_king
        )
        is_invalid_move = not chess_piece.validate_move(current_pos, target_pos)
        is_target_outside_path = target_pos not in path

        if is_king_checked and (is_invalid_move or is_target_outside_path):
            return standart_output

        King.last_checked_king = ""

    def is_checkmate(self, move: str, board: dict, king_identifier: str) -> bool:
        """Check if the current position results in checkmate."""

        king_position = None
        king_color = "white" if king_identifier[0] == "W" else "black"

        for position, piece in board.items():
            if piece == king_identifier:
                king_position = position
                break

        if not king_position:
            return False

        current_col = self.column_labels.index(king_position[0])
        current_row = int(king_position[1])

        move_directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
        ]

        if not King.is_king_in_check(board, king_color, king_identifier):
            return False

        self.path = get_path_between_positions(move, king_position)

        for cell in self.path:
            for position, piece in board.items():
                if piece == "empty":
                    continue

                if piece[0] == king_color[0].upper() and piece[1] != "K":
                    piece_class = self.piece_classes[piece[1]]
                    chess_piece = piece_class(king_color, board)

                    if chess_piece.validate_move(position, cell):
                        return False

        for col_delta, row_delta in move_directions:
            new_col = current_col + col_delta
            new_row = current_row + row_delta

            if 0 <= new_col <= 7 and 1 <= new_row <= 8:
                new_position = self.column_labels[new_col] + str(new_row)

                # Validates neighbor cells, meaning can the king go there in first place and if the cell isn't under check
                temp_board = board.copy()
                temp_board[king_position] = "empty"
                temp_board[new_position] = king_identifier

                king = King(king_color, board)

                # If cells around are all blocked or under check it's meaning that the king is checkmated
                if king.validate_move(king_position, new_position):
                    if not King.is_king_in_check(
                        temp_board, king_color, king_identifier
                    ):
                        return False

        return True

    def handle_promotion_choice(self, board: dict) -> dict | None:
        black_pawn_on_first_rank = next(
            (
                letter + "1"
                for letter in self.column_labels
                if board[letter + "1"] == "BP"
            ),
            None,
        )
        white_pawn_on_last_rank = next(
            (
                letter + "8"
                for letter in self.column_labels
                if board[letter + "8"] == "WP"
            ),
            None,
        )

        return white_pawn_on_last_rank or black_pawn_on_first_rank

    def handle_move(
        self, current_pos: str, target_pos: str, piece: str, board: dict
    ) -> dict:
        """Validate a chess move and check for checkmate conditions."""

        standart_output = self.output.copy()

        standart_output["processed_cell"] = target_pos

        if not all([current_pos, target_pos, piece, board]):
            return standart_output

        if not (len(current_pos) == 2 and len(target_pos) == 2):
            return standart_output

        piece_color = "white" if piece.startswith("W") else "black"
        opponent_color = "white" if piece_color == "black" else "black"

        king = piece[0] + "K"
        enemy_king = opponent_color[0].upper() + "K"

        piece_class = self.piece_classes.get(piece[1])

        if not piece_class:
            return standart_output

        chess_piece = piece_class(piece_color, board)

        # Create a copy of the board with the moved piece
        updated_board = board.copy()
        updated_board[current_pos] = "empty"
        updated_board[target_pos] = piece

        in_check_status = King.is_king_in_check(updated_board, piece_color, king)
        enemy_in_check_status = King.is_king_in_check(
            updated_board, piece_color, enemy_king
        )

        promotion = self.handle_promotion_choice(board)

        if promotion:
            pawn = promotion

            promo_board = board.copy()
            promo_board[pawn] = piece

            checkmate_with_promotion = self.is_checkmate(
                target_pos, promo_board, enemy_king
            )

            standart_output["check"] = enemy_in_check_status
            standart_output["checkmate"] = checkmate_with_promotion
            standart_output["winner"] = piece_color

            return standart_output

        # * Enables for sides to move in order (white then black)
        # if piece[0] == self.last_side_to_move:
        #     return standart_output

        if chess_piece.validate_move(current_pos, target_pos, in_check_status):

            in_check_before_moving = self.handle_check(
                current_pos, target_pos, chess_piece
            )

            if in_check_before_moving: 
                return in_check_before_moving 

            checkmate_status = self.is_checkmate(target_pos, updated_board, "WK")
            if not checkmate_status:
                checkmate_status = self.is_checkmate(target_pos, updated_board, "BK")

            return {
                "move_valid": True,
                "checkmate": checkmate_status,
                "winner": piece_color,
                "check": enemy_in_check_status,
                "processed_cell": target_pos,
                "en_passant": Pawn.is_en_passant,
            }

        return standart_output
