class Player():
    def __init__(self, player_id: str, stake: int, folded: bool, chips: int):
        self.player_id = player_id
        self.stake = stake
        self.folded = folded
        self.chips = chips
