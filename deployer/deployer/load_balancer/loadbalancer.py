# chose a random server from machines.json
import json
import random
import importlib.resources as pkg_resources
import logging
import socket
logging.basicConfig(level=logging.INFO)

servers = pkg_resources.read_binary('deployer.load_balancer', 'machines.json')
servers = json.loads(servers)
logging.info('Machines details loaded from machines.json')


def get_server():
    return random.choice(servers)


def get_free_port(host):
    while True:
        port = random.randint(32768, 61000)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not (sock.connect_ex((host, port)) == 0):
            return port


if __name__ == '__main__':
    print(get_server())
