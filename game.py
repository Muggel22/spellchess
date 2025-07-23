import chess
from board import print_board
from spells import SpellEngine
from bot import Bot

class SpellChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.spells = SpellEngine()
        self.bot = Bot(self.board, self.spells)

    def play(self):
        while not self.board.is_game_over():
            self.player_turn()
            if self.board.is_game_over():
                break
            self.bot_turn()

    def player_turn(self):
        color = "white"
        print_board(self.board)
        print(f"🧙 {color.upper()} am Zug – Spells: {self.spells.get_status(color)}")
        move = input("Eingabe (z. B. jump@d2 Bf4+ oder e4): ").strip()
        self.board.push_san(move)  # stark vereinfacht

    def bot_turn(self):
        move = self.bot.decide_action()
        self.board.push(move)
        print(move)