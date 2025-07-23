import chess

def draw_board(board, spell_engine, turn_counter):
    print("\n    a   b   c   d   e   f   g   h")
    print("  +---+---+---+---+---+---+---+---+")
    for r in range(7, -1, -1):
        row = f"{r+1} |"
        for c in range(8):
            sq = chess.square(c, r)
            piece = board.piece_at(sq)
            if spell_engine.is_frozen(sq, turn_counter):
                row += " # |"
            elif piece:
                row += f" {piece.symbol()} |"
            else:
                row += "   |"
        print(row + f" {r+1}")
        print("  +---+---+---+---+---+---+---+---+")
    print("    a   b   c   d   e   f   g   h\n")
