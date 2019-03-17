
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

    def bet_setup(self):
        self.hand = []
        self.table = []
        self.ourChips = 0
        self.ourStake = 0
        self.oppStake = []
        self.oppChips = []
        self.blind = 0
        self.currBet = 0

        for card in self.bot.status["pocketCards"]:
            self.hand.append([card["rank"], card["suit"]])

        for player in self.bot.status["activePlayers"]:
            if player["playerId"] == self.bot.player_id:
                self.ourChips = player["chips"]
                self.ourStake = player["stake"]
            else:
                self.oppChips.append(player["chips"])
                self.oppStake.append(player["stake"])

        if self.oppStake:
            self.currBet = max(self.oppStake)
        self.blind = self.bot.status["blind"]

        if "communityCards" in self.bot.status.keys():
            for card in self.bot.status["communityCards"]:
                self.table.append([card["rank"], card["suit"]])

    def decide_bet(self):
        self.bet_setup()
        if self.bot.round_num == 1:
            self.bluff = False
            self.FirstRound()
        # TODO: Need to add table
        elif self.bot.round_num == 2:
            self.Flop()
        elif self.bot.round_num == 3:
            self.Turn()
        elif self.bot.round_num == 4:
            self.River()
        else:
            print "ERROR: We done fucked up"

    # Action helpers
    def raiseIt(self, amount):
        print "Raising by ", amount
        self.bot.bet_response("raise", False, amount)

    def fold(self):
        print "Folding"
        if self.ourStake == self.currBet:
            self.bot.bet_response("check", False)
        else:
            self.bot.bet_response("fold", False)

    def call(self):
        print "Calling"
        if self.ourStake != self.currBet:
            self.bot.bet_response("call", False)
        else:
            self.bot.bet_response("check", False)

    def bully(self, opponentsChips, ferocity):
        print "bullying "
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
        strength = self.handRank(hand)
        if strength > n:
            quality = 0
        elif strength < m:
            quality = 2
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

        # Bluffing
        if randint(0,b)==0:
            self.bluff = True
            self.raiseIt(self.currBet)
            return

        # Bullying
        shouldBully, chipNo = False, 0 
        for chips in self.oppChips: #Make sure this is only for players still in
            if chips/self.ourChips < x: # oppChips:ourChips ratio
                shouldBully = True
                if chips > chipNo:
                    chipNo = chips #Highest no. of chips we want to bully with
        if shouldBully:
            self.bully(chipNo, f)
            
        # TODO: introduce randomness
        # If the bet is too large 
        if (self.currBet - self.ourStake) > (self.blind * 2):
            # TODO: keep track of who is doing big fuck off bets
            self.fold()
        elif self.checkHoldingShit():
           self.fold()
        elif self.checkHoldingGold():
             # TODO: We should raise, we are holding gold
            self.call()
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
    


    def Flop(self):
        # Parameters to tune
        m = 2000 # Threshold for strength
        n = 7000 # Threshold for weakness
        c = 0.2  # Threshold for us to fold on a medium hand
        d = 0.1  # Threshold for us to fold on a weak hand

        x = 0.2  # Threshold to initiate bullying
        f = 0.5  # Ferocity of bullying

        oppHandStrength = [1/i for i in self.getOppHandRank()]
        ownStrength = 1/self.evaluateHand(n, m, self.hand)
        likelihood = mean(oppHandRank) - 


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

        # Bluffing
        elif randint(0,5)==0: # Bluff on 1/6 rounds
            self.raiseIt(randint(1, self.ourChips))

        # Points at which we'll throw in the towel based on our own hand strength
        elif ((self.currBet/self.ourChips) > c and ownStrength != 2) or ((self.currBet/self.ourChips) > d and ownStrength == 0):
            self.fold()

        elif (self.handRank(self.hand) < likelihood):
            self.raiseIt(self.currBet*0.5)
        else:
            print "ERROR: no condition met folding"
            self.fold()




    def Turn(self):
        # Parameters to tune
        m = 2000 # Threshold for strength
        n = 7000 # Threshold for weakness
        c = 0.2  # Threshold for us to fold on a medium hand
        d = 0.1  # Threshold for us to fold on a weak hand

        x = 0.2  # Threshold to initiate bullying
        f = 0.5  # Ferocity of bullying

        oppHandStrength = [1/i for i in self.getOppHandRank()]
        ownStrength = 1/self.evaluateHand(n, m, self.hand)
        likelihood = mean(oppHandRank)-1.5*std(oppHandRank)

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

        # Bluffing
        elif randint(0,5)==0: # Bluff on 1/6 rounds
            self.raiseIt(randint(1,ourChips))

        # Points at which we'll throw in the towel based on our own hand strength
        elif ((self.currBet/self.ourChips) > c and ownStrength != 2) or ((self.currBet/self.ourChips) > d and ownStrength == 0):
            self.fold()

        elif (self.handRank(hand) < likelihood):
            self.raiseIt(currBet*0.5)
        else:
            print "ERROR: no condition met folding"
            self.fold()

    def River(self):
        # Parameters to tune
        m = 2000 # Threshold for strength
        n = 7000 # Threshold for weakness
        c = 0.2  # Threshold for us to fold on a medium hand
        d = 0.1  # Threshold for us to fold on a weak hand

        x = 0.2  # Threshold to initiate bullying
        f = 0.5  # Ferocity of bullying

        oppHandRank = self.getOppHandRank()
        ownStrength = self.evaluateHand(n, m, self.hand)


        # Bullying
        shouldBully, chipNo = False, 0 
        for chips in self.oppChips: #Make sure this is only for players still in
            if chips/self.ourChips < x: # oppChips:ourChips ratio
                shouldBully = True
                if chips > chipNo:
                    chipNo = chips #Highest no. of chips we want to bully with
        if shouldBully:
            self.bully(chipNo, f)

        # If we're the big or small blind then silly to bet (unless bullying)
        elif self.outStake == self.currBet:
            self.call()

        # Bluffing
        elif randint(0,5) == 0: # Bluff on 1/6 rounds
            self.raiseIt(randint(1, self.ourChips))

        # Points at which we'll throw in the towel based on our own hand strength
        elif ((self.currBet/self.ourChips) > c and ownStrength != 2) or ((self.currBet/self.ourChips) > d and ownStrength == 0):
            self.fold()

        elif (self.handRank(hand) < mean(oppHandRank)-1.5*std(oppHandRank)):
            self.raiseIt(currBet*0.5)
        else:
            print "ERROR: no condition met folding"
            self.fold()