class SpellEngine:
    def __init__(self):
        self.state = {
            "white": {"cooldown": 0, "last": None, "used": {"freeze": 0, "jump": 0}},
            "black": {"cooldown": 0, "last": None, "used": {"freeze": 0, "jump": 0}}
        }

    def get_status(self, color: str) -> str:
        status = self.state[color]
        return f"Cooldown={status['cooldown']}, Letzter Spell={status['last']}, Verwendet={status['used']}"