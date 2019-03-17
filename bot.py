from status import Status
import json
from connect import MySocket


from card import Card
from evaluator import Evaluator


class Bot(object):
    def __init__(self):
        self.sock = MySocket()
        self.status = {}
        self.prev_winning_hand = -1
        self.winners = []
        self.rank={}
        self.rank["ace"] = 'A'
        self.rank["king"] = "K"
        self.rank["queen"] = "Q"
        self.rank["jack"] = "J"
        self.rank["10"] = 'T'
        self.rank["9"] = '9'
        self.rank["8"] = '8'
        self.rank["7"] = '7'
        self.rank["6"] = '6'
        self.rank["5"] = '5'
        self.rank["4"] = '4'
        self.rank["3"] = '3'
        self.rank["2"] = '2'
        self.suit = {}
        self.suit["diamonds"] = 'd'
        self.suit["hearts"] = 'h'
        self.suit["clubs"] = 'c'
        self.suit["spades"] = 's'
        self.player_id = "name_id"
        self.round_num = -1

        

    def login(self, is_tournament):
        msg = { "type": "login",
        "player": "Pogodite",
        "tournament": is_tournament
        }
        self.sock.send(msg)
        
        while True:
            data = self.sock.receive()
            if data["type"] == "login_response":
                break
        self.update_status(data)
        self.player_id = self.status["playerId"]

    def auction_response(self, super_power_name= "",  bid= 0):
        if super_power_name == "":
            msg = { "type": "action_response",
                    "token": self.status['token'],
            }
        else:
            msg = { "type": "action_response",
                    "token": self.status['token'],
                    "superPower": super_power_name,
                    "bid": bid
            }
        self.sock.send(msg)

    def bet_response(self, action, use_reserve, stake = 0):
        print 'in bet response'
        print action
        if action == "raise":
            msg = { "type": "bet_response",
                    "token": self.status['token'],
                    "action": action,
                    "stake": stake,
                    "useReserve": use_reserve
            }
        else:
            msg = { "type": "bet_response",
                    "token": self.status['token'],
                    "action": action,
                    "useReserve": use_reserve
            }
            print msg
        self.sock.send(msg)

    def auction_received(self): 
        data = self.sock.receive()
        self.update_status(data)
        #check type!!!!
        

    def auction_result(self):
        data = self.sock.receive()
        self.update_status(data)
    
    def receive(self):
        data = self.sock.receive()
        if not data:
            return
        self.update_status(data)
        if "communityCards" in self.status.keys():
            table_card_count = len(self.status["communityCards"])
        else:
            table_card_count = 0

        if table_card_count == 0:
            self.round_num = 1
        elif table_card_count == 3:
            self.round_num = 2
        elif table_card_count == 4:
            self.round_num = 3
        elif table_card_count == 5:
            self.round_num = 4

        print "recieved type: " + data['type']
        if data['type'] == "bet":
            return "bet"
        elif data['type'] == "summary":
            self.round_num = 0
            return "summary"
        elif data['type'] == "status":
            return "status"
        elif data['type']=='auction':
            return "auction"
        elif data['type']=="auction_result":
            return 'auction_result'
        elif data['type']=="folded":
            return 'folded'
        elif data['type']=="bankrupt":
            return 'bankrupt'
        elif data['type']=="super_power":
            return 'super_power'
        else:
          # We do not know the message print it out
          print "what is this!!!!"
          print data

    def bet_received(self, json_data):
        self.status.bet_token = json_data["token"]
    
    # Only used when we request to use a super_power
    # The card that has been seen with spy/seer, or added to pocket
    def super_power_response(self, json_data):
        self.update_status(data)


    def summary_received(self, json_data):
        self.prev_winning_hand = json_data["hand"]
        self.winners = json_data["winners"]
    
    def bankrupt_received(self, json_data):
        pass
    
    def receive_status(self):
        data = self.sock.receive()
        self.update_status(data)

    def update_status(self, json_data):

        for key in json_data.keys():
            self.status[key]=json_data[key]

    def nice_show_status(self):
        keys = self.status.keys()
        important = ["hand","stake","pocketCards","communityCards"]
        #pocket cards is a list of cards
        #communityCards is a list of cards
        print "#"*40
        print "current type:\t {}".format(self.status["type"])
        print
        if "hand" in keys:
            print "Current hand:\t{}".format(self.status["hand"])
            print
        if "blind" in keys:
            print "Current blind:\t {}".format(self.status["blind"])  
            # print      
        hand=[]
        table=[]                        
        if "pocketCards" in keys:
            cards=[]
            for card in self.status["pocketCards"]:
                cards.append(self.to_deuces(card["suit"], card["rank"]))
            print("Our hand:")                
            Card.print_pretty_cards(cards)
            hand=cards                                                            
            print
        if "communityCards" in keys:
            cards=[]
            for card in self.status["communityCards"]:
                cards.append(self.to_deuces(card["suit"], card["rank"]))
            print("on the table:")
            Card.print_pretty_cards(cards)
            table = cards
            print
        if "communityCards" in keys and table and hand:
            e=Evaluator()
            print "Score of hand is:\t {}".format(e.evaluate(hand, table))
        print
        if "pot" in keys:
            print "current pot\t{}".format(self.status["pot"])
        print "We are " + self.player_id
        print
        print "Players:"
        print
        if "activePlayers" in keys:
            for player in self.status["activePlayers"]:
                print "Player ID = ", player["playerId"]
                print "stake = ", player["stake"]
                print "folded = ", player["folded"]
                print "chips = ", player["chips"]
                print

        print "-"*40
      
    def show_winner(self):
        keys = self.status.keys()
        if "winners" in keys:
            for winner in self.status["winners"]:
                winner_keys = winner.keys()
                print "Player ID = ", winner["playerId"], " has won!"
                print "Chips won = ", winner["chips"]
                
                if "bestHand" in winner_keys:
                    print "Best hand(s):"
                    best_cards=[]
                    for card in winner["bestHand"]:
                        best_cards.append(self.to_deuces(card["suit"], card["rank"]))
                    if best_cards:
                        Card.print_pretty_cards(best_cards)

    def to_deuces(self, suit, rank):
        return Card.new(self.rank[rank] + self.suit[suit])
            
        
          

