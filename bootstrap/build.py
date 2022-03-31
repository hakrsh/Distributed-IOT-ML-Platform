import docker
import json
import logging

logging.basicConfig(level=logging.INFO)

services = json.loads(open('config.json').read())
logging.info('load config.json')

client = docker.from_env()
for service in services['services']:
    image = client.images.build(path=service['path'], tag=f'{service["name"]}:{service["version"]}')[0]
    logging.info('build image ' + service['name']+':'+service['version'])
    with open(f'{service["name"]}_{service["version"]}.tar', 'wb') as f:
        for chunk in image.save(chunk_size=1024):
            f.write(chunk)
    logging.info('save image to file')


