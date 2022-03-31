import docker
from requests import get
import json
import socket
import logging

logging.basicConfig(level=logging.INFO)

host_ip = get('https://api.ipify.org').content.decode('utf8')
host_name = socket.gethostname()
# write ip to deployer/config.json
data = json.load(open('deployer/config.json'))
data['host_ip'] = host_ip
data['host_name'] = host_name
with open('deployer/config.json', 'w') as outfile:
    json.dump(data, outfile)
logging.info('Host IP: ' + host_ip)
logging.info('Host Name: ' + host_name)
logging.info('Updating config.json')

client = docker.from_env()
logging.info('Connected to Docker')
logging.info('Starting build')
client.images.build(path='.', tag='deployer')
logging.info('Built image: deployer')
try:
    container = client.containers.get('deployer')
    logging.info('Container exists, stopping')
    container.stop()
    logging.info('Removing container: deployer')
    container.remove()
except:
    logging.info('Container does not exist')
logging.info('Creating container: deployer')
try:
    client.containers.run('deployer',name='deployer', detach=True, network='host', volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}})
except Exception as e:
    logging.info('Error: ' + str(e))
logging.info('Started deployer')