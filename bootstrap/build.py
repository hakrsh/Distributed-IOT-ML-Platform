import docker
import json
import logging

logging.basicConfig(level=logging.INFO)

services = json.loads(open('config.json').read())
logging.info('load config.json')

client = docker.from_env()
output_tar_file = f"{services['tar_file']}_{services['version']}.tar"
for service in services['services']:
    image_name = f'{service["name"]}:{service["version"]}'
    logging.info('building image ' + image_name)
    image = client.images.build(path=service['path'], tag=image_name)[0]
    logging.info('build image ' + image_name)
    logging.info('adding image ' + image_name + ' to tar file ' + output_tar_file)
    with open(output_tar_file, 'wb') as f:
        for chunk in image.save(chunk_size=1024):
            f.write(chunk)
    logging.info('Added image ' + image_name + ' to tar file ' + output_tar_file)
    


