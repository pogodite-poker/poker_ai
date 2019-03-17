# This is a comment 

import socket
import json

TCP_IP="35.197.236.148"
TCP_PORT = 9877

BUFFER_SIZE=1024


data={"type":"login", "player":"Pogodite", "tournament":False}
MESSAGE = json.dumps(data)

header = len(MESSAGE).to_bytes(4, "little")
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect((TCP_IP,TCP_PORT))

s.sendall(header)
s.sendall(MESSAGE.encode())

data=s.recv(BUFFER_SIZE)
print(repr(data))

s.close()

