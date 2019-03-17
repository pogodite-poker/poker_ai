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
    bot.login(True)
    print("logged in")


    while bot.sock.is_connected:
        # TODO: need to do the below until the end of the betting
        # Need to wait for status 
        print("waiting for message")
        b = bot.receive()
        print(b)
        # Get power auction.
        # Recieve auction token
        if b == "auction":
            print("Got auction")
            play.decide_auction()
            # bot.auction_response()
            print("responding to auction")
        
        elif b == "auction_result":
            print("Got auction result")
        
        elif b == "bet":
            print("received bet")
            play.decide_bet()
            print("responding to bet")
    
            # TODO: If power add later
        elif b == "summary":
            print("received summary")
            bot.show_winner()


            
            # TODO:
            # output summary to the user
            # break
        elif b == "bankrupt":
            print("we fucked it...")
            bot.sock.disconnect()
            break
        elif b == "folded":
            print "we have folded"
        elif b == "status": 
            print "receive status"
            bot.nice_show_status()
            # Receive bankrupt if we fucked it
        elif b == "super_power": 
            print("Received super_power")
        elif not b:
            print("is empty!!!")
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