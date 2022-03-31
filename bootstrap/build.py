from concurrent.futures import thread
import docker
import json
import logging
import threading

logging.basicConfig(level=logging.INFO)

services = json.loads(open('config.json').read())
logging.info('load config.json')

client = docker.from_env()
def build(tag):
    logging.info('building image ' + tag)
    image = client.images.build(path=service['path'], tag=tag)[0]
    logging.info('build image ' + tag)
    logging.info('saving image ' + tag)
    with open(f'{tag}.tar', 'wb') as f:
        for chunk in image.save(chunk_size=1024):
            f.write(chunk)
    logging.info('save image to file')

for service in services['services']:
    tag = f'{service["name"]}:{service["version"]}'
    build(tag)
#     build_threads = []
#     logging.info('start build thread')
#     t = threading.Thread(target=build, args=(tag,))
#     build_threads.append(t)
#     t.start()

# for t in build_threads:
#     t.join()    
    


