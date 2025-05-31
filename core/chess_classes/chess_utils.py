from .chess_pieces import Rook, King

def get_path_between_positions(start: str, end: str) -> list:
    """Calculate the path between two positions on the board. Including the starting cell"""

    letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
    path = []

    start_col, start_row = letters.index(start[0]), int(start[1])
    end_col, end_row = letters.index(end[0]), int(end[1])

    path.append(start)

    # Return path with horse posiiton if it attacks the king
    if abs(end_col - start_col) == 2 and abs(end_row - start_row) == 1:
        return path

    elif abs(end_col - start_col) == 1 and abs(end_row - start_row) == 2:
        return path

    col_step = 0 if start_col == end_col else (1 if start_col < end_col else -1)
    row_step = 0 if start_row == end_row else (1 if start_row < end_row else -1)

    current_col, current_row = start_col + col_step, start_row + row_step

    while (
        0 <= current_col <= 7
        and 1 <= current_row <= 8
        and letters[current_col] + str(current_row) != end
    ):
        path.append(letters[current_col] + str(current_row))
        current_col += col_step
        current_row += row_step

    return path

def update_rook_move_count(old_cell: str, piece: str) -> None:

    if piece[1] != "R":
        return None

    if old_cell == "a8":
        Rook.black_left_move_count += 1
    elif old_cell == "h8":
        Rook.black_right_move_count += 1
    elif old_cell == "a1":
        Rook.white_left_move_count += 1
    elif old_cell == "h1":
        Rook.white_right_move_count += 1


def update_king_move_count(piece: str) -> None:
    if piece[1] != "K":
        return None

    if piece[0] == "W":
        King.white_move_count += 1
    else:
        King.black_move_count += 1