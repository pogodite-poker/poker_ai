class Status():

    def __init__(self):
        self.hand = -1
        self.blind = -1
        self.pot = -1
        self.stake = -1
        self.current_player = ""
        self.pocket_cards = []
        # Super powers below number represents the amount of powers you have
        self.super_power = []
        self.community_cards = []
        self.roles = ""
        self.active_players = []
        self.bankrupt_players = []
        
        # Auction token
        self.auction_token = -1

        # Bet token
        self.bet_token = -1

        # When we use super powers
        self.card_seen = []
        # super power info 