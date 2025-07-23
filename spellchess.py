import chess
import chess.engine
import re

STOCKFISH_PATH = r"C:\Users\matth\Downloads\stockfish\stockfish.exe"  # ← Pfad ggf. anpassen

class Spell:
    def __init__(self):
        self.cooldowns = {"white": 0, "black": 0}
        self.last_spell = {"white": None, "black": None}
        self.freeze_zone = None  # (center_square, valid_until_turn)

    def can_cast(self, color, spell):
        return (
            self.cooldowns[color] == 0
            and self.last_spell[color] != spell
        )

    def tick(self, color):
        if self.cooldowns[color] > 0:
            self.cooldowns[color] -= 1

    def is_frozen(self, square, current_turn):
        if not self.freeze_zone:
            return False
        center, valid_until = self.freeze_zone
        if current_turn >= valid_until:
            self.freeze_zone = None
            return False
        r1, c1 = divmod(center, 8)
        r2, c2 = divmod(square, 8)
        return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1

class SpellChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.spells = Spell()
        self.turn_counter = 0
        self.jump_active = {"white": False, "black": False}
        self.move_log = []

    def draw_board(self):
        print("\n    a   b   c   d   e   f   g   h")
        print("  +---+---+---+---+---+---+---+---+")
        for r in range(7, -1, -1):
            row = f"{r+1} |"
            for c in range(8):
                sq = chess.square(c, r)
                piece = self.board.piece_at(sq)
                if self.spells.is_frozen(sq, self.turn_counter):
                    row += " # |"  # frozen zone
                elif piece:
                    row += f" {piece.symbol()} |"
                else:
                    row += "   |"
            print(row + f" {r+1}")
            print("  +---+---+---+---+---+---+---+---+")
        print("    a   b   c   d   e   f   g   h\n")

    def get_color(self):
        return "white" if self.board.turn == chess.WHITE else "black"

    def parse_spell_and_move(self, input_str):
        match = re.match(r"(?:\s*(jump|freeze)@([a-h][1-8]))?\s*([a-hKQRNBx0-9=+#-]{2,})", input_str.strip())
        if not match:
            raise ValueError("❌ Ungültige Eingabe. Format: [spell@feld] Zug")
        spell, square, move = match.groups()
        return spell, square, move.strip()

    def is_valid_jump(self, move):
        dx = (move.to_square % 8) - (move.from_square % 8)
        dy = (move.to_square // 8) - (move.from_square // 8)
        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)
        count = 0
        cur = move.from_square
        for _ in range(7):
            r, c = divmod(cur, 8)
            r += step_y
            c += step_x
            if 0 <= r < 8 and 0 <= c < 8:
                cur = r * 8 + c
                if cur == move.to_square:
                    break
                if self.board.piece_at(cur):
                    count += 1
            else:
                return False
        return count == 1

    def player_turn(self):
        color = self.get_color()
        self.spells.tick(color)
        print(f"🧙 {color.upper()} am Zug – Spells (Cooldown: {self.spells.cooldowns[color]}):")
        available_spells = [s for s in ["jump", "freeze"] if self.spells.can_cast(color, s)]
        print("Verfügbare Spells:", " ".join([f"{s}@<feld>" for s in available_spells]) or "Keine")

        user_input = input("Eingabe (z. B. jump@d2 Bf4+ oder e4): ").strip()
        try:
            spell, target_square, move_str = self.parse_spell_and_move(user_input)
        except ValueError as e:
            print(str(e))
            exit(1)

        if spell:
            if not self.spells.can_cast(color, spell):
                print(f"❌ {spell} ist nicht erlaubt (Cooldown oder Wiederholung)")
                exit(1)
            if spell == "freeze":
                try:
                    sq = chess.parse_square(target_square)
                    self.spells.freeze_zone = (sq, self.turn_counter + 1)
                    print(f"🧊 {color} wirkt FREEZE auf {target_square}")
                except:
                    print("❌ Ungültiges Freeze-Feld")
                    exit(1)
            elif spell == "jump":
                self.jump_active[color] = True
                print(f"🌀 {color} aktiviert JUMP von {target_square}")
            self.spells.cooldowns[color] = 3
            self.spells.last_spell[color] = spell
        else:
            self.spells.last_spell[color] = None

        try:
            move = self.board.parse_san(move_str)
        except Exception as e:
            print(f"❌ Ungültiger Zug: {e}")
            exit(1)

        if self.spells.is_frozen(move.from_square, self.turn_counter):
            print("❄️ Dein Startfeld ist eingefroren!")
            exit(1)
        if self.spells.is_frozen(move.to_square, self.turn_counter):
            print("❄️ Dein Zielfeld ist eingefroren!")
            exit(1)
        if self.jump_active[color] and not self.is_valid_jump(move):
            print("❌ Jump ungültig – es muss genau 1 Figur übersprungen werden!")
            exit(1)

        self.board.push(move)
        self.move_log.append((color, spell, move_str))
        self.jump_active[color] = False

    def bot_turn(self):
        color = self.get_color()
        self.spells.tick(color)
        print("🤖 Bot denkt...")

        result = self.engine.play(self.board, chess.engine.Limit(time=1))
        move = result.move

        if self.spells.is_frozen(move.from_square, self.turn_counter) or \
           self.spells.is_frozen(move.to_square, self.turn_counter):
            print("❄️ Bot-Zug blockiert durch Freeze – überspringt Zug!")
            self.move_log.append((color, None, "❄️ pass"))
            return

        try:
            san = self.board.san(move)        # VOR push holen
            self.board.push(move)
            self.move_log.append((color, None, san))
            print(f"🤖 Bot zieht: {san}")
        except Exception as e:
            print(f"❌ Fehler beim Bot-Zug: {e}")
            exit(1)

    def print_move_log(self):
        print("\n📜 Zugverlauf:")
        for i in range(0, len(self.move_log), 2):
            white = self.move_log[i]
            black = self.move_log[i + 1] if i + 1 < len(self.move_log) else None
            line = f"{i//2 + 1}. "
            line += f"{white[1]+'@' if white[1] else ''}{white[2]}"
            if black:
                line += f"    {black[1]+'@' if black[1] else ''}{black[2]}"
            print(line)
        print()

    def play(self):
        print("✨ Willkommen bei Spell Chess! ✨")
        while not self.board.is_game_over():
            self.draw_board()
            if self.board.turn == chess.WHITE:
                self.player_turn()
            else:
                self.bot_turn()
            self.turn_counter += 1

        self.draw_board()
        print("🏁 Spiel beendet:", self.board.result())
        self.print_move_log()
        self.engine.quit()

if __name__ == "__main__":
    game = SpellChessGame()
    game.play()
