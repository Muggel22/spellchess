import chess

class SpellEngine:
    def __init__(self):
        self.active_spell = None
        self.freeze_zone = None
        self.freeze_active_until_turn = None

    def apply_spell(self, board, spell_name, square, current_turn):
        square = chess.parse_square(square)
        spell_name = spell_name.lower()
        if spell_name == "freeze":
            self.freeze_zone = self._get_freeze_zone(square)
            self.freeze_active_until_turn = current_turn + 1  # Freeze gilt exakt 1 gegnerischen Zug lang
            self.active_spell = "freeze"
        elif spell_name == "jump":
            # Jump hat keinen dauerhaften Effekt
            self.active_spell = "jump"

    def _get_freeze_zone(self, center_square):
        # Return a set of squares in the 3x3 zone centered on the given square.
        x = chess.square_file(center_square)
        y = chess.square_rank(center_square)
        zone = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx = x + dx
                ny = y + dy
                if 0 <= nx <= 7 and 0 <= ny <= 7:
                    zone.add(chess.square(nx, ny))
        return zone

    def is_frozen(self, square, current_turn):
        # Return True if the square is currently frozen.
        if self.freeze_zone and self.freeze_active_until_turn is not None:
            if current_turn <= self.freeze_active_until_turn:
                return square in self.freeze_zone
        return False

    def clear_expired_freeze(self, current_turn):
        if self.freeze_active_until_turn is not None and current_turn > self.freeze_active_until_turn:
            self.freeze_zone = None
            self.freeze_active_until_turn = None