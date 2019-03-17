# Used to connect to the tcp poker server

import json
import time
import socket
import struct
import pickle
import select
TCP_IP="35.197.236.148"
TCP_PORT = 9877

BUFFER_SIZE=1024

message = "Hello, World!"

from socket import SHUT_RDWR

MSGLEN = 1024

def to_bytes(n, length, endianess='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if endianess == 'big' else s[::-1]

class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """
    
    def __init__(self):

        self.sock = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect(("35.197.236.148",9877))
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.is_connected = True

    def send(self, msg):
        d=json.dumps(msg)
        """ Sends messgaes to the server """
        encoded=d.encode()
        header = to_bytes(len(encoded), 4, "little")
        self.sock.sendall(header)
        self.sock.send(encoded)

    def receive(self):
        """ Recieves messages from the server """
        raw_data = self.sock.recv(4)
        print raw_data
        if not raw_data:
            return
        length = int(struct.unpack("<i", raw_data)[0])
        data = json.loads(self.sock.recv(length))
        # print(data)
        return data

    def disconnect(self):
        self.is_connected = False
        self.sock.close()

    def empty_socket(self):
        """remove the data present on the socket"""
        input = [self.sock]
        while 1:
            inputready, o, e = select.select(input,[],[], 0.0)
            if len(inputready)==0: break
            for s in inputready: s.recv(1)









