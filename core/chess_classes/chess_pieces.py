class Piece:
    """Base class for all pieces"""

    last_moved_piece = ("piece", "old_cell", "new_cell")

    black_move_count = 0
    white_move_count = 0
    letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
    rows = ["1", "2", "3", "4", "5", "6", "7", "8"]

    def __init__(self, name, weight, side, grid):
        self.name = name
        self.weight = weight
        self.side = side
        self.grid = grid
        self.enemy_side = "white" if self.side == "black" else "black"

    def __str__(self):
        return self.name


class Rook(Piece):

    white_left_move_count = white_right_move_count = 0
    black_left_move_count = black_right_move_count = 0

    def __init__(self, side, grid):
        super().__init__("Rook", 5, side, grid)

    def validate_move(
        self, current_position: str, target_position: str, is_check: bool = None
    ) -> bool:
        """
        Checks whether the rook can move to or attack the target_position

        Arguments:
            current_position: str, like 'a5'
            target_position: str

        Returns:
            bool
        """

        if is_check == True:
            return False

        cur_row, tar_row = int(current_position[1]), int(target_position[1])
        cur_col, tar_col = current_position[0], target_position[0]

        if cur_col != tar_col and cur_row != tar_row:
            return False  # Rooks cannot move diagonally

        # Determine the direction and range to check
        if cur_row == tar_row:  # Horizontal move
            start_idx = self.letters.index(cur_col)
            end_idx = self.letters.index(tar_col)

            # Ensure proper direction (left to right or right to left)
            step = 1 if start_idx < end_idx else -1

            for i in range(start_idx + step, end_idx, step):  # Check cells in between
                intermediate_pos = self.letters[i] + str(cur_row)
                if self.grid[intermediate_pos] != "empty":
                    return False

        elif cur_col == tar_col:  # Vertical move
            start_row = min(cur_row, tar_row) + 1
            end_row = max(cur_row, tar_row)

            for row in range(start_row, end_row):  # Check cells in between
                intermediate_pos = cur_col + str(row)
                if self.grid[intermediate_pos] != "empty":
                    return False

        # Check the target position
        if self.grid[target_position] == "empty":
            return True
        elif self.grid[target_position][0] != self.side[0].upper():  # Enemy piece
            return True

        return False


class Pawn(Piece):

    is_en_passant = False

    def __init__(self, side, grid):
        super().__init__("Pawn", 1, side, grid)

    def en_passant(self, current_position: str, target_position: str) -> bool:

        cur_col, cur_row = self.letters.index(current_position[0]), int(
            current_position[1]
        )
        tar_col, tar_row = self.letters.index(target_position[0]), int(
            target_position[1]
        )

        direction = 1 if self.side == "white" else -1

        if self.side == "white":
            if cur_row != 5:
                return False
        else:
            if cur_row != 4:
                return False

        # Check if the target_position is the en passant cell
        if abs(cur_col - tar_col) != 1 or (cur_row + direction) != tar_row:
            return False

        piece, old_cell, new_cell = self.last_moved_piece

        # Check whether the piece to capture en passant is enemy
        if piece[0] == self.side[0].upper() or piece[1] != "P":
            return False

        pawn_col_old_cell, pawn_row_old_cell = self.letters.index(old_cell[0]), int(
            old_cell[1]
        )
        pawn_col_new_cell = self.letters.index(new_cell[0])

        # Checks if the enemy pawn made double jump (from a2 to a4)
        if (
            abs(cur_col - pawn_col_old_cell) != 1
            or cur_row + (direction * 2) != pawn_row_old_cell
        ):
            return False

        if tar_col != pawn_col_new_cell:
            return False

        Pawn.is_en_passant = True

        return True

    def validate_move_sideways(
        self, current_position: str, target_position: str
    ) -> bool:
        """
        Checks whether the pawn can attack the nearby cells

        Arguments:
            current_position: str, like 'g6'
            target_position: str

        Returns:
            bool
        """

        row = current_position[1]
        char = current_position[0]

        index = self.letters.index(char)

        # Looks for neighboring cells
        neighbors = []

        if index > 0:  # There's a left neighbor
            neighbors.append(self.letters[index - 1])

        if index < len(self.letters) - 1:  # There's a right neighbor
            neighbors.append(self.letters[index + 1])

        # Adjusts which way the pawn should attack
        if self.side == "black":
            row = f"{int(row) - 1}"

        else:
            row = f"{int(row) + 1}"

        for neighbor in neighbors:

            if (
                neighbor + row == target_position
                and self.grid[target_position] != "empty"
            ):
                if self.grid[target_position][0] != self.side[0].upper():
                    return True

        return False

    def validate_move_forward(
        self, current_position: str, target_position: str
    ) -> bool:
        """
        Decides whether the pawn can move to the front cell
        Also checks if the pawn can make two cells move

        Arguments:
            current_position: str, like 'h4'
            target_position: str

        Returns:
            bool
        """

        row = int(current_position[1])
        char = current_position[0]

        if self.side == "black":
            direction = -1

        else:
            direction = 1

        if direction == -1 and row == 1:
            return False
        elif direction == 1 and row == 8:
            return False

        # If the cell in front of the pawn isn't empty then return False
        if self.grid[char + str(row + direction)] != "empty":
            return False

        # If pawn is white and it's first move of the pawn then let it go to 4 row
        if self.side == "white" and row == 2:
            if (
                char + str(row + 2) == target_position
                and self.grid[target_position] == "empty"
            ):
                return True

        if self.side == "black" and row == 7:
            if (
                char + str(row - 2) == target_position
                and self.grid[target_position] == "empty"
            ):
                return True

        # Checks whether the front cell is the target_position
        if char + str(row + direction) == target_position:
            return True

        return False

    def validate_move(
        self, current_position: str, target_position: str, is_check: bool = None
    ) -> bool:

        if is_check == True:
            return False

        if self.validate_move_forward(current_position, target_position):
            return True
        elif self.validate_move_sideways(current_position, target_position):
            return True

        return self.en_passant(current_position, target_position)


class Horse(Piece):
    def __init__(self, side, grid):
        super().__init__("Horse", 3, side, grid)

    def validate_move(
        self, current_position: str, target_position: str, is_check: bool = None
    ) -> bool:

        if is_check == True:
            return False

        cur_col, cur_row = self.letters.index(current_position[0]), int(
            current_position[1]
        )
        tar_col, tar_row = self.letters.index(target_position[0]), int(
            target_position[1]
        )

        if self.grid[target_position][0] == self.side[0].upper():
            return False

        if abs(tar_col - cur_col) == 2 and abs(tar_row - cur_row) == 1:
            return True

        elif abs(tar_col - cur_col) == 1 and abs(tar_row - cur_row) == 2:
            return True

        return False


class Bishop(Piece):
    def __init__(self, side, grid):
        super().__init__("Bishop", 3, side, grid)

    def validate_move(
        self, current_position: str, target_position: str, is_check: bool = None
    ) -> bool:

        if is_check == True:
            return False

        cur_row, tar_row = int(current_position[1]), int(target_position[1])
        cur_col, tar_col = self.letters.index(current_position[0]), self.letters.index(
            target_position[0]
        )

        col_step = 0 if cur_col == tar_col else (1 if cur_col < tar_col else -1)
        row_step = 0 if cur_row == tar_row else (1 if cur_row < tar_row else -1)

        if abs(col_step) != 1 or abs(row_step) != 1:
            return False

        while True:

            cur_col += col_step
            cur_row += row_step

            if not (0 <= cur_col <= 7 and 1 <= cur_row <= 8):
                break

            new_position = self.letters[cur_col] + str(cur_row)

            if new_position == target_position:
                if (
                    self.grid[new_position] == "empty"
                    or self.grid[new_position][0] != self.side[0].upper()
                ):
                    return True

                return False

            if self.grid[new_position] != "empty":
                break

        return False


class Queen(Piece):
    def __init__(self, side, grid):
        super().__init__("Queen", 9, side, grid)

    def validate_move(
        self, current_position: str, target_position: str, is_check: bool = None
    ) -> bool:
        # Essentially queen validate_move method is
        # rook's and bishop's validate_move methods combined

        if is_check == True:
            return False

        rook = Rook(self.side, self.grid)
        bishop = Bishop(self.side, self.grid)

        if rook.validate_move(current_position, target_position, is_check):
            return True

        return bishop.validate_move(current_position, target_position, is_check)


class King(Piece):

    last_checked_king = ""
    enemy_check_position = ""

    def __init__(self, side, grid):
        super().__init__("King", 0, side, grid)
        # I can also put the weight as float('inf')

    @classmethod
    def is_stalemate(
        cls, board: dict, king_identifier: str = None
    ) -> bool: # pragma: no cover
        """Checks every neighboring cell around the king for stalemate"""

        raise NotImplementedError
        # Someday...

    @classmethod
    def is_king_in_check(
        cls,
        board: dict,
        king_color: str,  # ? Do I need it
        king_identifier: str = None,  # ? maybe it doesn't need to be set to None
        check_use: bool = None,
    ):
        """
        Check if a given king is in check.

        Arguments:
            board: dictionary instance, consiting of cells and their state
            king_color: king's color, string ('white' or 'black')
            king_identifier: string, like 'WK' or 'BK'
            check_use: boolean value, tells the method should it set the class variables to the corresponding piece and position

        Returns:
            bool
        """

        king_position = ""

        if King.last_checked_king:
            king_identifier = King.last_checked_king

        for position, piece in board.items():
            if piece == king_identifier:
                king_position = position
                break

        if not king_position:
            return False

        piece_classes = {
            "R": Rook,
            "P": Pawn,
            "K": King,
            "Q": Queen,
            "H": Horse,
            "B": Bishop,
        }

        if king_identifier[0] == "W":
            enemy_color = "black"
        elif king_identifier[0] == "B":
            enemy_color = "white"
        else: # pragma: no cover
            enemy_color = "black" if king_color == "white" else "white"

        for position, piece in board.items():
            if piece == "empty":
                continue

            if piece[0] == enemy_color[0].upper():
                piece_type = piece[1]
                piece_class = piece_classes.get(piece_type)

                if piece_class:
                    enemy_piece = piece_class(enemy_color, board)
                    if enemy_piece.__class__.__name__ == "Pawn":
                        if enemy_piece.validate_move_sideways(position, king_position):
                            # So that when just waving around the piece it wouldn't trigger King.last_checked_king = ...
                            if check_use == True:
                                King.last_checked_king = king_identifier
                                King.enemy_check_position = position
                            return True

                    elif enemy_piece.validate_move(position, king_position):
                        if check_use == True:
                            King.last_checked_king = king_identifier
                            King.enemy_check_position = position
                        return True

        return False

    def _is_cell_safe(self, current_position: str, cell_position: str) -> bool:
        """Helper method inteded to be used in castle method"""

        moved = self.grid.copy()
        moved[current_position] = "empty"
        moved[cell_position] = self.side[0].upper() + "K"
        piece_name = moved[cell_position]

        if King.is_king_in_check(moved, self.side, piece_name):
            return True

        return False

    def castle(self, current_position: str, target_position: str) -> bool:
        current_move_count = self.black_move_count
        if self.side == "white":
            current_move_count = self.white_move_count

        if current_move_count != 0:
            return False

        cur_col = self.letters.index(current_position[0])
        tar_col = self.letters.index(target_position[0])

        king_position = "e1"
        long_castle_rook_position = "a1"
        short_castle_rook_posiiton = "h1"

        color = self.side[0].upper()

        if self.side == "black":
            king_position = "e8"
            long_castle_rook_position = "a8"
            short_castle_rook_posiiton = "h8"

        if current_position != king_position:
            return False
        
        # Can't castle when in check
        if self._is_cell_safe(target_position, current_position):
            return False

        # Short castle
        if tar_col > cur_col:
            if self.grid[short_castle_rook_posiiton] != color + "R":
                return False

            if self.side == "white":
                if Rook.white_right_move_count != 0:
                    return False
            else:
                if Rook.black_right_move_count != 0:
                    return False

            g_cell = "g" + king_position[1]
            f_cell = "f" + king_position[1]

            # Checks if the f cell is under attack
            if self._is_cell_safe(current_position, f_cell):
                return False
            elif self._is_cell_safe(current_position, g_cell):
                return False

            if self.grid[f_cell] != "empty" or self.grid[g_cell] != "empty":
                return False

            if (
                target_position == short_castle_rook_posiiton
                or target_position == "g" + short_castle_rook_posiiton[1]
            ):
                return True

        # Long castle
        elif tar_col < cur_col:    
            if self.grid[long_castle_rook_position] != color + "R":
                return False

            if self.side == "white":
                if Rook.white_left_move_count != 0:
                    return False
            else:
                if Rook.black_left_move_count != 0:
                    return False

            b_cell = "b" + king_position[1]
            c_cell = "c" + king_position[1]
            d_cell = "d" + king_position[1]

            # Checks if the d cell is under attack
            if self._is_cell_safe(current_position, d_cell):
                return False
            elif self._is_cell_safe(current_position, c_cell):
                return False

            if (
                self.grid[b_cell] != "empty"
                or self.grid[c_cell] != "empty"
                or self.grid[d_cell] != "empty"
            ):
                return False

            if (
                target_position == long_castle_rook_position
                or target_position == "c" + long_castle_rook_position[1]
            ):
                return True
        
        return False

    def validate_king_move(self, current_position: str, target_position: str) -> bool:
        """
        Validates if the king can move to the target position.
        The king can move one square in any direction, but cannot move into check.
        """

        cur_row = int(current_position[1])
        cur_col = self.letters.index(current_position[0])
        tar_row = int(target_position[1])
        tar_col = self.letters.index(target_position[0])

        # Check if the move is within one square in any direction
        if abs(cur_row - tar_row) > 1 or abs(cur_col - tar_col) > 1:
            return False

        # Check if target position is occupied by a friendly piece
        if (
            self.grid[target_position] != "empty"
            and self.grid[target_position][0] == self.side[0].upper()
        ):
            return False

        return True

    def validate_move(
        self, current_position: str, target_position: str, is_check: bool = None
    ) -> bool:

        if is_check == True:
            return False

        elif self.validate_king_move(current_position, target_position):
            return True

        return self.castle(current_position, target_position)
