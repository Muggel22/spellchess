class Bot:
    def __init__(self, board, spells):
        self.board = board
        self.spells = spells

    def decide_action(self):
        return list(self.board.legal_moves)[0]