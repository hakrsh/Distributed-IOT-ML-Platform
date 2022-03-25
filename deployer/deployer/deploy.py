import docker
from deployer.load_balancer import loadbalancer
import logging

logging.basicConfig(level=logging.INFO)


def Deploy(path, container_name):
    server = loadbalancer.get_server()
    url = 'ssh://' + server['user'] + '@' + server['ip'] + ':' + server['port']
    logging.info('Connecting to: ' + url)
    client = docker.DockerClient(base_url=url)
    logging.info('Connected to: ' + url)
    logging.info('Building the image')
    client.images.build(path=path, tag=container_name+':latest')
    logging.info('Built image: ' + container_name)
    try:
        container = client.containers.run(
            container_name+':latest', detach=True, network_mode='host')
    except:
        logging.info('Container already running')
        container = client.containers.get(container_name)
        container.restart()
        logging.info('Restarted container: ' + container_name)
    logging.info('Container: ' + container_name +
                 ' status: ' + container.status)
    return {
        'container_id': container.id,
        'conatiner_name': container.name,
        'container_status': container.status
    }
