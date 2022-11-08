# chose a random server from machines.json
import random
import logging
import socket
logging.basicConfig(level=logging.INFO)


def get_free_port():
    while True:
        port = random.randint(32768, 61000)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex(('127.0.0.1', port)): # returns non-zero if connection is unsuccessful -> port is free
            return port
        else:
            sock.close()
