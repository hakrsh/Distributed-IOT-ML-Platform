import docker
from deployer.load_balancer import loadbalancer
import logging
from deployer import module_config
import os
import shutil
import requests
logging.basicConfig(level=logging.INFO)


def Deploy(dockerfile_path, image_tag, instance_id, package):
    client = docker.from_env()
    logging.info('Building image: ' + image_tag)
    client.images.build(path=dockerfile_path, tag=image_tag)
    logging.info('Built image: ' + image_tag)
    port = loadbalancer.get_free_port()
    logging.info('Free port: ' + str(port))
    logging.info('Creating container: ' + image_tag)
    container = client.containers.run(
        image_tag, detach=True, ports={'80': port})
    container = client.containers.get(container.id)
    logging.info('Container: ' + container.id +
                 ' status: ' + container.status)
    res = {
        'port': port,
        'container_id': container.id,
        'container_status': container.status,
        'host_ip': module_config['host_ip'],
        'host_name': module_config['host_name']
    }
    logging.info('Deployed instance: ' + instance_id)
    os.remove(f'/tmp/{package}.zip')
    logging.info('Removed temporary file: /tmp/'+package+'.zip')
    shutil.rmtree(f'/tmp/{package}/')
    logging.info('Removed temporary directory /tmp/'+package+'/')
    requests.post(module_config['deployer_master']+'/deployed', json={
        'instance_id': instance_id,
        'res': res
    })
    logging.info('Sent update to master')


def stopInstance(container_id,instance_id):
    logging.info('Got stop request for instance: ' + instance_id)
    logging.info('Connecting to Docker')
    client = docker.from_env()
    logging.info('Getting container: ' + container_id)
    container = client.containers.get(container_id)
    logging.info('Stopping container: ' + container_id)
    container.stop()
    logging.info('Stopped container: ' + container_id)
    logging.info('Removing container: ' + container_id)
    container.remove()
    logging.info('Removed container: ' + container_id)
    requests.post(module_config['deployer_master']+'/stopped', json={'instance_id': instance_id, 'container_status': 'stopped'})
    logging.info('Sent update to master')
    
