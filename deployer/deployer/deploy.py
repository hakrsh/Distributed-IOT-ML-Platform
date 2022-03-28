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
    logging.info('Building image: ' + image_tag)
    client.images.build(path=dockerfile_path, tag=image_tag)
    logging.info('Built image: ' + image_tag)
    port = loadbalancer.get_free_port(server['ip'])
    logging.info('Free port: ' + str(port))
    logging.info('Creating container: ' + image_tag)
    container = client.containers.run(
        image_tag, detach=True, ports={'80': port})
    container = client.containers.get(container.id)
    logging.info('Container: ' + container.id +
                 ' status: ' + container.status)
    return {
        'ip': server['ip'],
        'port': port,
        'container_id': container.id,
        'container_status': container.status
    }
