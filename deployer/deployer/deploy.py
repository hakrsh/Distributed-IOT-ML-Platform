from time import sleep
import docker
from deployer.load_balancer import loadbalancer
import logging

logging.basicConfig(level=logging.INFO)


def Deploy(dockerfile_path, image_tag):
    server = loadbalancer.get_server()
    url = 'ssh://' + server['user'] + '@' + server['ip'] + ':' + server['port']
    logging.info('Connecting to: ' + url)
    client = docker.DockerClient(base_url=url)
    logging.info('Connected to: ' + url)
    if client.images.list(name=image_tag):
        logging.info('Image already exists: ' + image_tag)
    else:
        logging.info('Image does not exist: ' + image_tag)
        logging.info('Building image: ' + image_tag)
        client.images.build(path=dockerfile_path, tag=image_tag)
        logging.info('Built image: ' + image_tag)

    container = client.containers.run(
        image_tag, detach=True, network_mode='host')
    container = client.containers.get(container.id)
    logging.info('Container: ' + container.id +
                 ' status: ' + container.status)
    return {
        'ip': server['ip'],
        'container_id': container.id,
        'container_status': container.status
    }
