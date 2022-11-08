# chose a random server from machines.json
import random
import logging
import socket
logging.basicConfig(level=logging.INFO)


def get_free_port():
    while True:
        port = random.randint(32768, 61000)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex(('127.0.0.1', port)): # returns 0 if connection is successful -> port is not free
            return port
