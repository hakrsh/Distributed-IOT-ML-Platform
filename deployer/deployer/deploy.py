import docker
from deployer.load_balancer import loadbalancer

def Deploy(path, container_name):
    server = loadbalancer.get_server()
    url = 'ssh://' + server['user'] + '@' + server['ip'] + ':' + server['port']
    print('url: ' + url)
    client = docker.DockerClient(base_url=url)
    client.images.build(path=path, tag=container_name+':latest')
    print('image built successfully')
    try:
        container = client.containers.run(container_name+':latest', detach=True,network_mode='host')  
    except:
        print("Container already exists")
        container = client.containers.get(container_name)
        container.restart()
    return {
        'container_id': container.id,
        'conatiner_name': container.name,
        'container_status': container.status
    }
