import docker
from requests import get
import json
import socket

host_ip = get('https://api.ipify.org').content.decode('utf8')
host_name = socket.gethostname()
# write ip to deployer/config.json
data = json.load(open('deployer/config.json'))
data['host_ip'] = host_ip
data['host_name'] = host_name
with open('deployer/config.json', 'w') as outfile:
    json.dump(data, outfile)

client = docker.from_env()
client.images.build(path='.', tag='deployer')
client.containers.run('deployer', detach=True, net='host', volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}})