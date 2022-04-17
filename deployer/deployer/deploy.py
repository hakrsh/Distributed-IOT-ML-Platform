import threading
import docker
from deployer.load_balancer import loadbalancer
import logging
from deployer import module_config
import os
import shutil
import requests
from deployer import db
logging.basicConfig(level=logging.INFO)



def Deploy(dockerfile_path, image_tag, instance_id, package,job_id):
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
    db.instances.update_one({"instance_id": instance_id}, {"$set": {
                            "status": res['container_status'],
                            "container_id": res['container_id'],
                            "hostname": res['host_name'],
                            "ip": res['host_ip'],
                            "port": res['port']}})
    logging.info('Updated instance db status')
    # requests.post(module_config['deployer_master']+'/deployed', json={
    #     'instance_id': instance_id,
    #     'res': res
    # })
    # logging.info('Sent update to master')
    db.jobs.update_one({'job_id': job_id}, {"$set": {'status': 'done'}})


def stopInstance(container_id, instance_id, job_id):
    logging.info('Got stop request for instance: ' + instance_id)
    logging.info('Connecting to Docker')
    client = docker.from_env()
    logging.info('Getting container: ' + container_id)
    try:
        container = client.containers.get(container_id)
        logging.info('Stopping container: ' + container_id)
        container.stop()
        logging.info('Stopped container: ' + container_id)
        logging.info('Removing container: ' + container_id)
        container.remove()
        logging.info('Removed container: ' + container_id)
    except Exception:
        logging.info('Container not found')
    # requests.post(module_config['deployer_master']+'/stopped',
    #               json={'instance_id': instance_id, 'container_status': 'stopped'})
    # logging.info('Sent update to master')
    db.instances.delete_one({"instance_id": instance_id})
    db.jobs.update_one({'_id': job_id}, {"$set": {'status': 'done'}})
    logging.info('Removed instance from db')

def calculate_mem_percentage(stats):
    mem_used = stats["memory_stats"]["usage"] - stats["memory_stats"]["stats"]["cache"] + \
        stats["memory_stats"]["stats"]["active_file"]
    limit = stats['memory_stats']['limit']
    return round(mem_used / limit * 100, 2)


def calculate_cpu_percentage(stats):
    cpu_stats = stats['cpu_stats']
    total_usage = cpu_stats['cpu_usage']['total_usage']
    system_cpu_usage = cpu_stats['system_cpu_usage']
    cpu_percent = (total_usage / system_cpu_usage) * 1000
    return round(cpu_percent, 2)


def get_container_data(container):
    stat = container.stats(stream=False)
    temp = {}
    temp['container_id'] = container.id
    temp['image_name'] = container.attrs['Config']['Image']
    temp['cpu_usage'] = calculate_cpu_percentage(stat)
    temp['mem_usage'] = calculate_mem_percentage(stat)
    return temp


def systemStats():
    logging.info('Getting system status')
    client = docker.from_env()
    logging.info('Connecting to Docker')
    stats = []
    threads = []
    for container in client.containers.list():
        t = threading.Thread(target=lambda: stats.append(
            get_container_data(container)))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    logging.info('Got system status')
    return stats
