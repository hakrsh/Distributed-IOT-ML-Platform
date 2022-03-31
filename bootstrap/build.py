from concurrent.futures import thread
from tkinter import image_names
import docker
import json
import logging
import tarfile

logging.basicConfig(level=logging.INFO)

services = json.loads(open('config.json').read())
logging.info('load config.json')

client = docker.from_env()
def build(image):
    logging.info('building image ' + image)
    image = client.images.build(path=service['path'], tag=image)[0]
    logging.info('build image ' + image)
    logging.info('saving image ' + image)
    with open(f'{image}.tar', 'wb') as f:
        for chunk in image.save(chunk_size=1024):
            f.write(chunk)
    logging.info('save image to file')
    return image + '.tar'

for service in services['services']:
    image = f'{service["name"]}:{service["version"]}'
    images = []
    images.append(build(image))
    output_tar_file = f"{services['tar_file']}_{service['version']}.tar"
    with tarfile.open(output_tar_file, 'w') as tar:
        for image in images:
            tar.add(image)

    


