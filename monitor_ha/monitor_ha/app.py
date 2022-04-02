from monitor_ha.config import module_config
import pymongo
import logging
import threading
import time
import docker


logging.basicConfig(level=logging.INFO)

mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

db = client[ "repo" ]
instances = db["instances"]
logging.info('instance database created')

def app_handler(app_info):
	instance_id = app_info["instance_id"]
	container_id = app_info["container_id"]
	hostname = app_info["hostname"]
	ip = app_info["ip"]
	port = app_info["port"]
	client = docker.DockerClient(base_url="ssh://{}@{}".format(hostname, ip))
	while True:
		print(container_id)
		time.sleep(10)

def run():
	instance_cursor = instances.find({})
	thread_list = []
	for document in instance_cursor:
		thread = threading.Thread(target=app_handler, args=(document,))
		thread_list.append(thread)
		thread.start()
	for thread in thread_list:
		thread.join()