from http import client
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
        'ip': container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress'],
        'port': port,
        'container_id': container.id,
        'container_status': container.status
    }
    postDeploy(instance_id, package, res)


def stopInstance(instance_id):
    instance = db.instances.find_one({"instance_id": instance_id})
    logging.info('Stopping instance: ' + instance_id)
    client = docker.from_env()
    container = client.containers.get(instance['container_id'])
    container.stop()
    logging.info('Stopped instance: ' + instance_id)
    db.instances.update_one({"instance_id": instance_id}, {"$set": {
                            "status": "stopped"}})
    logging.info('Updated instance db status')
