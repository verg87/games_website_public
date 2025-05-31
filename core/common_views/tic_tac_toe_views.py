from django.shortcuts import render
from django.http import HttpResponse


def initialize_game(request) -> None:
    """Set up for game"""

    request.session["board"] = [" " for i in range(9)]
    request.session["current_player"] = "X"
    request.session["winner"] = None


def find_winner(tic_tac_toe: list) -> str:
    """Returns the winner of a tic tac toe game"""

    winning = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]
    for win in winning:
        position = [tic_tac_toe[win[0]], tic_tac_toe[win[1]], tic_tac_toe[win[2]]]
        if position == ["X", "X", "X"] or position == ["O", "O", "O"]:
            return position[0]

    if all(item in ["X", "O"] for item in tic_tac_toe):
        return "Stalemate"

    return None


def general_output(request, template_name, error_message=None) -> HttpResponse:
    """Retieves context variables"""

    context_data = {
        "board": request.session["board"],
        "current_player": request.session["current_player"],
        "winner": request.session["winner"],
        "error_message": error_message,
    }

    return render(request, template_name, context_data)


def change_players(request) -> None:
    """Changes the players"""
    
    if request.session["current_player"] == "X":
        request.session["current_player"] = "O"

    else:
        request.session["current_player"] = "X"