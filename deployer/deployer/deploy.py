import docker
from deployer.load_balancer import loadbalancer
import logging

logging.basicConfig(level=logging.INFO)


def Deploy(path, container_name):
    server = loadbalancer.get_server()
    url = 'ssh://' + server['user'] + '@' + server['ip'] + ':' + server['port']
    logging.info('Connecting to: {}'.format(url))
    client = docker.DockerClient(base_url=url)
    client.images.build(path=path, tag=container_name+':latest')
    logging.info('Built image: {}'.format(container_name))
    try:
        container = client.containers.run(
            container_name+':latest', detach=True, network_mode='host')
    except:
        logging.info('Container already running')
        container = client.containers.get(container_name)
        container.restart()
        logging.info('Restarted container: {}'.format(container_name))
    logging.info('Container: {}'.format(container_name),
                 ' status: {}'.format(container.status))
    return {
        'container_id': container.id,
        'conatiner_name': container.name,
        'container_status': container.status
    }
