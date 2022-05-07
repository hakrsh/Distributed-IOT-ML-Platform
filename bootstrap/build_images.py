import docker
import json
import logging
from jinja2 import Template
import shutil

logging.basicConfig(filename='bootstrap.log', level=logging.INFO, format='%(asctime)s: %(message)s')

services = json.loads(open('services.json').read())
dockerfile_template = Template(open('docker_template.j2').read())
client = docker.from_env()
logging.info('Logging to DockerHub...')
client.login(username=services['username'], password=services['password'])
logging.info('Login successful')

def prepare_build_context():
    logging.info('Setting up the context for building...')
    dynamic_scaling = input('Would you like to enable dynamic scaling? (yes/no) ')
    for service in services['services']:
        dockerfile_path = '../' + service['name'] + '/Dockerfile'
        with open(dockerfile_path, 'w') as outfile:
            outfile.write(dockerfile_template.render(service=service, dynamic_scaling=dynamic_scaling))
        logging.info('Wrote dockerfile to ' + dockerfile_path)
        shutil.copy('wait-for-it.sh', '../' + '/' + service['name'] + '/wait-for-it.sh')
        shutil.copy('wait-for-kafka.sh', '../' + '/' + service['name'] + '/wait-for-kafka.sh')
    logging.info('Ready to build')

def build():
    logging.info('Building images...')
    for service in services['services']:
        image_name = f'{services["username"]}/{service["name"]}:{service["version"]}'
        logging.info(f'Building image {image_name}')
        client.images.build(path=service["path"], tag=image_name)
        logging.info(f'Pushing image {image_name}')
        for line in client.images.push(image_name, stream=True, decode=True):
            logging.info(line)
        logging.info(f'Image {image_name} pushed successfully')
    logging.info('Build complete')

if __name__ == '__main__':
    prepare_build_context()
    build()