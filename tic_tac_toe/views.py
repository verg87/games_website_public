from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt 
import json
from core.common_views.tic_tac_toe_views import (
    initialize_game,
    find_winner,
    general_output,
    change_players,
)

# @csrf_exempt  
# def log_f5_event(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         print("F5 Key Press Detected:", data.get("message", "No message"))
#         return JsonResponse({"status": "success", "message": "F5 logged successfully"})
    
#     return JsonResponse({"status": "error", "message": "Invalid request"})
# TODO Make an f5 keydown event handler


class TicTacToeGame(LoginRequiredMixin, TemplateView):
    template_name = "tic_tac_toe.html"

    def post(self, request) -> HttpResponse:
        """The core of the game"""

        if "board" not in request.session:
            initialize_game(request)

        # Tries to parse cell_index from the request.POST
        try:
            cell_index = int(request.POST.get("cell_index", None))

        # If reset_button was clicked or cell_index is missing, reinitialize the game
        except TypeError:
            if "reset_button" in request.POST:
                initialize_game(request)
    
            return general_output(request, self.template_name)
  
        # If the chosen cell is empty, place the current player's symbol and switch players
        if request.session["board"][cell_index] not in ["X", "O"]:
            request.session["board"][cell_index] = request.session["current_player"]
            change_players(request)

        # Checks if the game is over. 
        # Seals any action in the game if it is.
        elif find_winner(request.session["board"]) is not None:
            return general_output(request, self.template_name)

        # If cell is taken, return an error message
        elif request.session["board"][cell_index] in ["X", "O"]:
            error_message = "You can't put your sign where it has already been placed"
            return general_output(request, self.template_name, error_message)

        request.session["winner"] = find_winner(request.session["board"])

        return general_output(request, self.template_name)

    def get(self, request) -> HttpResponse:
        """initializes the game and returns HttpResponse"""

        if "board" not in request.session:
            initialize_game(request)

        return general_output(request, self.template_name)
        
