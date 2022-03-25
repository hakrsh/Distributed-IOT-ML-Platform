# chose a random server from machines.json
import json
import random
import importlib.resources as pkg_resources
import logging
logging.basicConfig(level=logging.INFO)

servers = pkg_resources.read_binary('deployer.load_balancer', 'machines.json')
servers = json.loads(servers)
logging.info('Machines details loaded from machines.json')


def get_server():
    return random.choice(servers)


if __name__ == '__main__':
    print(get_server())
