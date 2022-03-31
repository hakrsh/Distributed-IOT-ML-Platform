import docker
import json
import logging

logging.basicConfig(level=logging.INFO)

services = json.loads(open('config.json').read())
logging.info('load config.json')

client = docker.from_env()
client.login(username=services['username'], password=services['password'])
logging.info('Creating tar file')

for service in services['services']:
    image_name = f'{service["name"]}:{service["version"]}'
    logging.info('building image ' + image_name)
    image = client.images.build(path=service['path'], tag=image_name)[0]
    logging.info('build image ' + image_name)
    client.images.push(image_name)
    logging.info('push image ' + image_name + ' to registry')
