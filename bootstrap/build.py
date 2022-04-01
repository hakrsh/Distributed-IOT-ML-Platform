import docker
import json
import logging

logging.basicConfig(level=logging.INFO)

services = json.loads(open('config.json').read())
logging.info('load config.json')

def build(host,path,image_tag,container_name):
    logging.info('Connecing to ' + host)
    client = docker.DockerClient(base_url=host)
    logging.info('Connected to Docker')
    logging.info('Building ' + image_tag)
    client.images.build(path=path, tag=image_tag)
    logging.info('Built image: ' + image_tag)
    try:
        container = client.containers.get(container_name)
        logging.info('Container exists, stopping')
        container.stop()
        logging.info('Removing container: ' + container_name)
        container.remove()
    except:
        logging.info('Container does not exist')
    logging.info('Creating container: ' + container_name)
    try:
        if container_name == 'deployer':
            client.containers.run(image_tag,name=container_name, detach=True, network='host', volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}})
        else:
            client.containers.run(image_tag,name=container_name, detach=True, network='host')
    except Exception as e:
        logging.info('Error: ' + str(e))
    logging.info('Started ' + container_name)


for service in services['services']:
    image_name = f'{service["name"]}:{service["version"]}'
    logging.info('building image ' + image_name)
    host = 'ssh://' + services['master']['user'] + '@' + services['master']['ip']
    # host = 'unix://var/run/docker.sock'
    if service['name'] == 'deployer':
        for worker in services['workers']:
            host = 'ssh://' + worker['user'] + '@' + worker['ip'] 
            data = json.load(open('../deployer/deployer/config.json'))
            data['host_ip'] = worker['ip']
            data['host_name'] = worker['user']
            with open('../deployer/deployer/config.json', 'w') as outfile:
                json.dump(data, outfile)
            logging.info('Updating config.json')
            build(host,service['path'],image_name,service['name'])
    else:
        build(host,service['path'],image_name,service['name'])
