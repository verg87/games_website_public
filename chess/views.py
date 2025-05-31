from django.shortcuts import render
from django.http import HttpRequest
from .models import Board

def chess_page(request: HttpRequest):
    template_name = 'chess.html'
    model = Board()

    if request.method == "POST":

        last_obj = model.initialize_board()

        if 'reset' in request.POST:
            model.reset_board(last_obj)
            return render(request, template_name)
        
    return render(request, template_name)
