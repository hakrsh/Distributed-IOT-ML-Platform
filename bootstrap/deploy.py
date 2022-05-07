import docker
import json
import logging
import sys
import subprocess

if len((sys.argv)) < 2:
    print('Usage: deploy.py <load_bala>')
    sys.exit(1)
logging.basicConfig(filename='bootstrap.log', level=logging.INFO, format='%(asctime)s: %(message)s')
logging.info('Starting deploy script')
logging.info('Reading config files')
services = json.loads(open('services.json').read())
servers = json.loads(open('platform_config.json').read())
load_balancer = sys.argv[1]

def deploy(host,image_name,container_name,config_path):
    logging.info('Deploying ' + container_name)
    logging.info('Connecing to ' + host)
    client = docker.DockerClient(base_url=host)
    logging.info('Connected to Docker')
    logging.info('Pulling image: ' + image_name)
    client.images.pull(image_name)
    logging.info('Pulled image: ' + image_name)
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
        container_config_path = f'/{container_name}/config.json'
        if container_name == 'deployer' or container_name == 'monitor_logger' :
            client.containers.run(image_name,name=container_name, detach=True, network='host', volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
            config_path: {'bind': container_config_path, 'mode': 'rw'}},restart_policy={'Name': 'on-failure', 'MaximumRetryCount': 3})
        elif container_name == "monitor_ha":
            client.containers.run(image_name,name=container_name, detach=True, network='host', volumes={f"/home/{servers['master']['user']}/.ssh": {'bind': '/root/.ssh', 'mode': 'rw'},
            config_path: {'bind': container_config_path, 'mode': 'rw'}},restart_policy={'Name': 'on-failure', 'MaximumRetryCount': 3})
        elif container_name == "platform_manager":
            client.containers.run(image_name,name=container_name, detach=True, network='host', volumes={f"/home/{servers['master']['user']}/.ssh": {'bind': '/root/.ssh', 'mode': 'rw'},
            config_path: {'bind': container_config_path, 'mode': 'rw'},
            f"/home/{servers['master']['user']}/platform_config.json": {'bind': '/platform_manager/platform_config.json', 'mode': 'rw'},
            f"/home/{servers['master']['user']}/services.json": {'bind': '/platform_manager/services.json', 'mode': 'rw'},
            f"/home/{servers['master']['user']}/.azure": {'bind': '/root/.azure', 'mode': 'rw'},
            '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}},
            restart_policy={'Name': 'on-failure', 'MaximumRetryCount': 3})
        else:
            client.containers.run(image_name,name=container_name, detach=True, network='host',
                                  volumes={config_path: {'bind': container_config_path, 'mode': 'rw'}},restart_policy={'Name': 'on-failure', 'MaximumRetryCount': 3})
    except Exception as e:
        logging.info('Error: ' + str(e))
    logging.info('Deployed ' + container_name)


def generate_service_config():
    logging.info('Generating service config')
    master_ip = servers['master']['ip']
    workers = []
    for worker in servers['workers']:
        temp = {}
        temp['name'] = worker['user']
        temp['ip'] = worker['ip']
        workers.append(temp)
    service_config = {
        "kafka_ip": master_ip,
        "kafka_port": "9092",
        "mongo_server": master_ip+":27017",
        "sensor_reg_api": "http://" + master_ip + ":7005/",
        "deployer_master": "http://" + master_ip + ":9999/",
        "load_balancer": "http://localhost:9899/",
        "platform_api": "http://" + master_ip + ":5000/",
        "scheduler": "http://" + master_ip + ":8210/",
        "model_req_handler": "http://" + master_ip + ":5050/",
        "workers": workers,
        "frequency": "10" 
    }
    if load_balancer == 'haproxy':
        logging.info('Using haproxy')
        service_config['load_balancer'] = "http://localhost:9898/"
    logging.info('Writing config')
    with open('../config.json', 'w') as f:
        json.dump(service_config, f, indent=4)
    
    # for service in services['services']:
    #     config_path = '../' + service['name'] + '/' + service['name'] + '/config.json'
    #     with open(config_path, 'w') as outfile:
    #         json.dump(service_config, outfile)
    #     logging.info('Wrote service config to ' + config_path)
        
    logging.info('Copying config.json to master')
    cmd = 'scp ../config.json ' + servers['master']['user'] + '@' + servers['master']['ip'] + ':~/'
    subprocess.call(cmd, shell=True)
    logging.info('Copyied config to master')

def start_service():
    generate_service_config()
    logging.info('Starting services...')
    for service in services['services']:
        image_name = f'{services["username"]}/{service["name"]}:{service["version"]}'
        host = 'ssh://' + servers['master']['user'] + '@' + servers['master']['ip']
        # host = 'unix://var/run/docker.sock'
        if service['name'] == 'deployer' or service['name'] == 'monitor_logger'  or service['name'] == 'system_monitor':
            for worker in servers['workers']:
                host = 'ssh://' + worker['user'] + '@' + worker['ip'] 
                data = json.load(open('../config.json'))
                data['host_ip'] = worker['ip']
                data['host_name'] = worker['user']
                with open('../config.json', 'w') as outfile:
                    json.dump(data, outfile)
                logging.info('Updating config.json')
                cmd = 'scp ../config.json ' + worker['user'] + '@' + worker['ip'] + ':~/'
                logging.info('Copying config to worker')
                subprocess.call(cmd, shell=True)
                config_path = f'/home/{worker["user"]}/config.json'
                deploy(host,image_name,service['name'],config_path)
        else:
            config_path = f'/home/{servers["master"]["user"]}/config.json'
            deploy(host,image_name,service['name'],config_path)
    logging.info('Platform has been deployed ' + servers['master']['ip'] + ':2500')

if __name__ == '__main__':
    start_service()
