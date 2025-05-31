import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from ast import literal_eval
from core.chess_classes.chess_logic import ChessLogic
from .models import Board

class ChessConsumer(WebsocketConsumer):
    model = Board()
    game = ChessLogic()

    def connect(self):
        self.accept()

    def close(self, code=None):
        print(f"Closed connection with code: {code}")

    def receive(self, text_data=None):

        last_obj = self.model.initialize_board()
        board = literal_eval(last_obj.grid) if type(last_obj.grid) == str else {}

        data = json.loads(text_data)

        old_cell = data.get('oldCell')
        new_cell = data.get('newCell')
        piece = data.get('pieceMoved')
        event = data.get('eventType')
        castle = data.get('castle')
        promoted_to = data.get('pawnPromotedTo')

        move_info = self.game.handle_move(old_cell, new_cell, piece, board)
   
        if event == 'dragend' or event == 'click':
            if move_info['checkmate']:
                self.model.create_game(move_info['checkmate'])

            self.model.update_board(last_obj, old_cell, new_cell, piece, castle, promoted_to)
            
        async_to_sync(self.send(json.dumps(move_info))) # ? Maybe shouldn't do that