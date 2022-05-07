# For manual service restart

import docker
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
logging.info('Starting restart script')
logging.info('Reading config files')
servers = json.loads(open('platform_config.json').read())
services = json.loads(open('services.json').read())
client = docker.from_env()

def restart(image_name,container_name,config_path):
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
    logging.info('restarted ' + container_name)

images = []
containers = []
host = input('Enter host (master/worker): ')
config_path = f'/home/{servers[host]["user"]}/config.json'
for service in services['services']:
    images.append(f'{services["username"]}/{service["name"]}:{service["version"]}')
    containers.append(service['name'])
restart_all = input('Restart all containers? (y/n): ')
if restart_all == 'y':
    if host == 'master':
        for image in images:
            if image == f'{services["username"]}/deployer:{service["version"]}':
                continue
            restart(image,image.split('/')[1].split(':')[0],config_path)
    elif host == 'worker':
        image = f'{services["username"]}/deployer:{service["version"]}'
        restart(image,image.split('/')[1].split(':')[0],config_path)
else:
    if host == 'master':
        print('Select the service to restart:')
        for i in range(len(images)):
            print(str(i) + ': ' + containers[i])
        choice = int(input('Enter the number of the service to restart: '))
        restart(images[choice],containers[choice],config_path)
    elif host == 'worker':
        choice = input('Do u want to restart the deployer? (y/n): ')
        if choice == 'y':
            image = f'{services["username"]}/deployer:{service["version"]}'
            restart(image,image.split('/')[1].split(':')[0],config_path)
