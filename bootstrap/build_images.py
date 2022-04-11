import docker
import json
import logging

logging.basicConfig(filename='build.log', level=logging.INFO,filemode='w')
logging.info('Starting build')
logging.info('Reading config files')
services = json.loads(open('services.json').read())
client = docker.from_env()
client.login(username=services['username'], password=services['password'])
for service in services['services']:
    image_name = f'{services["username"]}/{service["name"]}'
    logging.info(f'Building image {image_name}')
    client.images.build(path=service["path"], tag=image_name)
    logging.info(f'Pushing image {image_name}')
    for line in client.images.push(image_name, stream=True, decode=True):
        logging.info(line)
    logging.info(f'Image {image_name} pushed successfully')
logging.info('Build complete')
