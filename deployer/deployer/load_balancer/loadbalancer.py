# chose a random server from machines.json
import json
import random
import importlib.resources as pkg_resources

servers = pkg_resources.read_binary('load_balancer', 'machines.json')
servers = json.loads(servers)

def get_server():
    return random.choice(servers)

if __name__ == '__main__':
    print(get_server())