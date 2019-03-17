
from random import randint
from bot import *
from evaluator import Evaluator
from numpy import mean, std
from card import Card

class Play():

    def __init__(self, bot):
        self.hand = []
        self.table = []
        self.ourChips = 0
        self.ourStake = 0
        self.oppChips = []
        self.oppStake = []
        self.blind = 0
        self.currBet = 0
        self.bot = bot
        self.bluff = False
        self.evaluator = Evaluator()
        self.leech_count = 0
        self.count_bet = 0

    def bet_setup(self):
        self.hand = []
        self.table = []
        self.ourChips = 0
        self.ourStake = 0
        self.oppStake = 0
        self.oppChips = []
        self.blind = 0
        self.currBet = 0
        keys = self.bot.status.keys()
        for card in self.bot.status["pocketCards"]:
            self.hand.append([card["rank"], card["suit"]])

        for player in self.bot.status["activePlayers"]:
            if player["playerId"] == self.bot.player_id:
                self.ourChips = player["chips"]
                self.ourStake = player["stake"]
            else:
                self.oppChips.append(player["chips"])

        if "communityCards" in keys:
            for card in self.bot.status["communityCards"]:
                self.table.append([card["rank"], card["suit"]])
      
    def decide_auction(self):
      # name, bid
      self.bot.auction_response("leech", randint(1, 3))

    def decide_bet(self):
        self.bet_setup()
        if self.bot.round_num == 1:
            # print "going into first round betting"
            self.count_bet = 0
            self.bluff = False
            self.FirstRound()
        # TODO: Need to add table
        elif self.bot.round_num == 2:
            #print "going into flop betting"
            self.Flop()
        elif self.bot.round_num == 3:
            #print "going into turn betting"
            self.Turn()
        elif self.bot.round_num == 4:
            #print "going into river betting"
            self.River()
        else:
            pass
            #print "ERROR: We done fucked up"

    # Action helpers
    def raiseIt(self, amount):
        self.oppStake = self.bot.status["stake"]
        #print "Raising by = ", amount
        self.count_bet = self.oppStake + amount 
        if amount < self.ourChips:
            self.bot.bet_response("raise", False, int(amount))
        else:
            self.call()

    def fold(self):
        # print "Folding/Checking"
        self.bot.bet_response("fold", False)

    def call(self):
        # print(self.bot.status)
        # print "calling"
        self.oppStake = int(self.bot.status["stake"])
        # if self.bot.round_num ==1:
        #     if self.bot.status["roles"]["bigBlind"] == self.bot.player_id:
        #         self.ourStake = int(self.bot.status["blinds"]["initialValue"]*2)
        #     elif self.bot.status["roles"]["smallBlind"] == self.bot.player_id:
        #         self.ourStake = int(self.bot.status["blinds"]["initialValue"])
        #     elif self.bot.status["roles"]["dealer"] == self.bot.player_id:
        #         self.ourStake = 0
        for player in self.bot.status["activePlayers"]:
            if player["playerId"] == self.bot.player_id:
                self.ourChips = player["chips"]
                self.ourStake = int(player["stake"])
            else:
                self.oppChips.append(player["chips"])
        self.currBet = int(self.oppStake) - int(self.ourStake)
        # print("currBet:", self.currBet)
        # print("ourStake:", self.ourStake)
        if self.currBet == 0:
            # print "Checking"
            self.bot.bet_response("check", False)
        else:
            # print "Calling"
            self.bot.bet_response("call", False)
    def bully(self, opponentsChips, ferocity):
        # print "bullying "
        self.bot.bet_response("raise", False, int(opponentsChips*ferocity))

    def handRank(self): # a has type [numeral,suit]
        # convert to deuces
        table_cards = []
        hand_cards = []

        for card in self.hand:
            hand_cards.append(self.bot.to_deuces(card[1], card[0]))
        for card in self.table:
            table_cards.append(self.bot.to_deuces(card[1], card[0]))
        return self.evaluator.evaluate(hand_cards, table_cards)

    def evaluateHand(self, n, m, hand):
        strength = 1/self.handRank()
        if strength > n:
            quality = 2
        elif strength < m:
            quality = 0
        else:
            quality = 1
        return quality

    def getOppHandRank(self):
        deuces_table = []
        for card in self.table:
            deuces_table.append(self.bot.to_deuces(card[1], card[0]))
        
        # Removing the cards on the table and in our hands from consideration
        deck = ['2D','3D','4D','5D','6D','7D','8D','9D','TD','JD','QD','KD','AD','2S','3S','4S','5S','6S','7S','8S','9S','TS','JS','QS','KS','AS','2H','3H','4H','5H','6H','7H','8H','9H','TH','JH','QH','KH','AH','2C','3C','4C','5C','6C','7C','8C','9C','TC','JC','QC','KC','AC']
        for card in (self.table + self.hand):
            if card[0] == "10":
                remove_card = ('T' + card[1][0].upper())
            else:
                remove_card = (card[0][0].upper() + card[1][0].upper())
            deck.remove(remove_card)

        opponentHandRanks = []
        for i in range(len(deck)):
            for j in range(i, len(deck)):
                if i != j:
                    oppHand = [Card.new(deck[i][0]+deck[i][1].lower()), Card.new(deck[j][0]+deck[j][1].lower())]
                    hand_strength = self.evaluator.evaluate(oppHand, deuces_table)
                    opponentHandRanks.append(hand_strength)
        return opponentHandRanks

    def checkHoldingShit(self):
        faceCards = ['ace','king','queen','jack']
        if self.hand[0][1] != self.hand[1][1]:
            if self.hand[0][0] != self.hand[1][0]:
                if self.hand[0][0] in faceCards or self.hand[1][0] in faceCards:
                    return False
                else:
                    card_1 = int(self.hand[0][0])
                    card_2 = int(self.hand[1][0])
                    if abs(card_2-card_1) > 5:
                        return True
                    else:
                        return False
            else:
                return False
        else:
            return False

    def checkHoldingGold(self):
        faceCards = ['ace','king','queen','jack']
        if self.hand[0][0] == self.hand[1][0]:
            if self.hand[0][0] in faceCards:
                return True
        return False

    def FirstRound(self):
        
        # Parameters to tune
        b = 4 # Bluff parameter

        x = 0.1  # Threshold to initiate bullying
        f = 0.5  # Ferocity of bullying
        '''
        # Bluffing
        if randint(0,b)==0:
            self.bluff = True
            self.raiseIt(self.currBet)
            return
        
        # Bullying
        shouldBully, chipNo = False, 0 
        for chips in self.oppChips: #Make sure this is only for players still in
            if chips/float(self.ourChips) < x: # oppChips:ourChips ratio
                shouldBully = True
                if chips > chipNo:
                    chipNo = chips #Highest no. of chips we want to bully with
        if shouldBully:
            self.bully(chipNo, f)
            
        # TODO: introduce randomness
        # If the bet is too large 
        '''
        if self.currBet > (self.blind * 2):
            # TODO: keep track of who is doing big fuck off bets
            self.fold()
        elif self.checkHoldingShit():
            self.fold()
        elif self.checkHoldingGold():
            # TODO: We should raise, we are holding gold
            self.raiseIt(randint(1, min(20, self.ourChips)))
            # self.call()
        else:
            # TODO: Need to check if call is correct or check
            self.call()
        return

        # # If we're the big or small blind then silly to bet (unless bullying)
        # elif stake==currBet:
        #     self.call()

        # # Points at which we'll throw in the towel based on our own hand strength
        # elif ((currBet/ourChips) > c and ownStrength != 2) or ((currBet/ourChips) > d and ownStrength == 0):
        #     self.fold()

        # elif (self.handRank(hand) < mean(oppHandRank)-1.5*std(oppHandRank)):
        #     self.raiseIt(currBet*0.5)
        
        # if(self.currBet<50):
        #     self.call()
        # else:
        #     self.fold()
    
    def super_power(self, name):
        self.bot.bet_response(name, False)

    def Flop(self):
        # Parameters to tune
        m = 1/7000 # Threshold for strength
        n = 1/4000 # Threshold for weakness
        c = 0.2  # Threshold for us to fold on a medium hand
        d = 0.1  # Threshold for us to fold on a weak hand

        x = 0.2  # Threshold to initiate bullying
        f = 0.5  # Ferocity of bullying

        #oppHandStrength = [1/i for i in self.getOppHandRank()]
        ownStrength = self.evaluateHand(n, m, self.hand)
        #likelihood = mean(oppHandStrength) - 1000

        '''
        # Bullying
        shouldBully, chipNo = False, 0 
        for chips in self.oppChips: #Make sure this is only for players still in
            if chips/self.ourChips < x: # oppChips:ourChips ratio
                shouldBully = True
                if chips > chipNo:
                    chipNo = chips #Highest no. of chips we want to bully with
        # TODO: add bullying and bluffing
        if abs(self.currBet - self.ourStake) > (self.blind * 4):
            self.bully(chipNo, f)
        '''
        # Use super powers
        if "superPowers" in self.bot.status.keys():
          # print self.bot.status["superPowers"]
          if self.bot.status["superPowers"]:
            if self.bot.status["superPowers"]["leech"] > 0:
                  self.bot.status["superPowers"]["leech"]  -= 1
                  self.super_power("leech")
                  # print "WE USED A SUPER POWER"
                  return

        # Bluffing
        #if (self.handRank() < likelihood):
        #    self.raiseIt(self.currBet*0.5)
        if ownStrength < 1:
            self.fold()
        # Points at which we'll throw in the towel based on our own hand strength
        elif ((self.currBet/self.ourChips) > c and ownStrength != 2) or ((self.currBet/self.ourChips) > d and ownStrength == 0):
            self.fold()
        elif randint(0,5)==0: # Bluff on 1/6 rounds
            self.raiseIt(randint(1, 20))
        elif (((self.currBet/self.ourChips) > d and ownStrength == 1) or ((self.currBet/self.ourChips) > c and ownStrength == 2)):
            self.call()
        else:
            # print "ERROR: no condition met call"
            self.call()




    def Turn(self):
        # Parameters to tune
        m = 1/7000 # Threshold for strength
        n = 1/4000 # Threshold for weakness
        c = 0.2  # Threshold for us to fold on a medium hand
        d = 0.1  # Threshold for us to fold on a weak hand

        x = 0.2  # Threshold to initiate bullying
        f = 0.5  # Ferocity of bullying

        #oppHandStrength = [1/i for i in self.getOppHandRank()]
        ownStrength = self.evaluateHand(n, m, self.hand)
        #likelihood = mean(oppHandStrength)-1000

        # # Bullying
        # shouldBully, chipNo = False, 0 
        # for chips in self.oppChips: #Make sure this is only for players still in
        #     if chips/self.ourChips < x: # oppChips:ourChips ratio
        #         shouldBully = True
        #         if chips > chipNo:
        #             chipNo = chips #Highest no. of chips we want to bully with

        # TODO: add bullying and bluffing
        #if self.handRank() < likelihood:
        #    self.raiseIt(self.currBet * 0.5)
        # Bluffing
        if randint(0,5) == 0: # Bluff on 1/6 rounds
            self.raiseIt(randint(1, min(20, self.ourChips)))
        elif ownStrength < 1:
            self.fold()
        # Points at which we'll throw in the towel based on our own hand strength
        elif ((self.currBet/self.ourChips) > c and ownStrength != 2) or ((self.currBet/self.ourChips) > d and ownStrength == 0):
            self.fold()
        
        elif (((self.currBet/self.ourChips) > d and ownStrength == 1) or ((self.currBet/self.ourChips) > c and ownStrength == 2)):
            self.call()
        
        else:
            # print "ERROR: no condition met calling"
            self.call()

    def River(self):
        # Parameters to tune
        m = 1/7000 # Threshold for strength
        n = 1/4000 # Threshold for weakness
        c = 0.2  # Threshold for us to fold on a medium hand
        d = 0.1  # Threshold for us to fold on a weak hand

        x = 0.2  # Threshold to initiate bullying
        f = 0.5  # Ferocity of bullying

        #oppHandStrength = [1/i for i in self.getOppHandRank()]
        ownStrength = self.evaluateHand(n, m, self.hand)
        #likelihood = mean(oppHandStrength)-1000
        
        #if self.handRank() < likelihood:
        #    self.raiseIt(self.currBet * 0.5)

        # If we're the big or small blind then silly to bet (unless bullying)
        if randint(0,5) == 0: # Bluff on 1/6 rounds
            self.raiseIt(randint(1, min(20, self.ourChips)))
        elif ownStrength < 1:
            self.fold()
        # Points at which we'll throw in the towel based on our own hand strength
        elif ((self.currBet/self.ourChips) > c and ownStrength != 2) or ((self.currBet/self.ourChips) > d and ownStrength == 0):
            self.fold()
        
        elif (((self.currBet/self.ourChips) > d and ownStrength == 1) or ((self.currBet/self.ourChips) > c and ownStrength == 2)):
            self.call()
        else:
            # print "ERROR: no condition met calling"
            self.call()