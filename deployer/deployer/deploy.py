import docker
from deployer.load_balancer import loadbalancer
import logging
from deployer import db
import os
import shutil
logging.basicConfig(level=logging.INFO)


def postDeploy(instance_id, package, res):
    logging.info('Deployed instance: ' + instance_id)
    os.remove(f'/tmp/{package}.zip')
    logging.info('Removed temporary file: /tmp/'+package+'.zip')
    shutil.rmtree(f'/tmp/{package}/')
    logging.info('Removed temporary directory /tmp/'+package+'/')
    # update instance status
    db.instances.update_one({"instance_id": instance_id}, {"$set": {
                            "status": res['container_status'],
                            "container_id": res['container_id'],
                            "ip": res['ip'],
                            "port": res['port']}})
    logging.info('Updated instance db status')


def Deploy(dockerfile_path, image_tag, instance_id, package):
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
    res = {
        'ip': server['ip'],
        'port': port,
        'container_id': container.id,
        'container_status': container.status
    }
    postDeploy(instance_id, package, res)
