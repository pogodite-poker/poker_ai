from bot import Bot
from time import sleep
import traceback
from play import Play
bot = Bot()
play = Play(bot)
first=True

bot.sock.empty_socket()



try:

    print("logging in")
    bot.login(False)
    print("logged in")


    while bot.sock.is_connected:
        # TODO: need to do the below until the end of the betting
        # Need to wait for status 
        print("waiting for message")
        b = bot.receive()
        
        # Get power auction.
        # Recieve auction token
        if b == "auction":
            print("Got auction")
            bot.auction_response()
            print("responding to auction")
        
        elif b == "auction_result":
            print("Got auction result")
        
        elif b == "bet":
            print("received bet")

            # TODO: make bet descision here
            
            # Bet response here
            
            play.decide_bet()
            # play.bet_setup()
            # if play.ourStake == play.currBet:
            #     bot.bet_response("check", False)
            # else:
            #     bot.bet_response("call", False)

            print("responding to bet")
    
            # TODO: If power add later
        elif b == "summary":
            print("received summary")
            bot.show_winner()
            print "test shit"

            if bot.status["winners"][0]["playerId"] != bot.player_id:
                print("We didn't win :(")
                for player in bot.status["activePlayers"]:
                    if player["playerId"] == bot.player_id:
                        chips_after = player["chips"]-player["stake"]
                        if chips_after<=0:
                            print("we done fucked it")
            # TODO:
            # output summary to the user
            # break
        elif b == "bankrupt":
            print("we fucked it...")
            bot.sock.disconnect()
            break
        elif b == "folded":
            print "We have folded, because we made a bobo"
        elif b == "status": 
            print("#"*30)
            bot.nice_show_status()
            print("#"*30)
            # Receive bankrupt if we fucked it

        elif not b:
            # print "b is empty" 
            # TODO: Look at recv being empty
            break
        else:
            print b
            raise Exception("ERROR: we don't know what we have received")
except Exception as e:
    print Exception,e
    pass
finally:
    bot.sock.disconnect()
traceback.print_exc()