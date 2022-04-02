from monitor_ha.config import module_config
import pymongo
import logging
import threading
import time
import docker

logging.basicConfig(level=logging.INFO)

monitor_interval = 1

mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

db = client[ "repo" ]
instances = db["instances"]
logging.info('instance database created')

def cleanup(client, instance_id, container_id):
	logging.info("Cleaning up {}".format(container_id))
	client.remove(container_id)

def recover(instance_id):
	logging.info("Recovering {}".format(container_id))

def app_handler(app_info):
	instance_id = app_info["instance_id"]
	container_id = app_info["container_id"]
	hostname = app_info["hostname"]
	ip = app_info["ip"]
	port = app_info["port"]
	try:
		client = docker.DockerClient(base_url="ssh://{}@{}".format(hostname, ip))
	except Exception as e:
		print("Could not connect to docker daemon")
	while True:
		try:
			cont = client.containers.get(container_id)
			cont_status = cont.status
			if cont_status != "running":
				logging.info("Container {} not running".format(container_id))
				cleanup(client, container_id)
				recover(instance_id)
		except Exception as e:
			print("Could not find any such container")
		time.sleep(monitor_interval)

def run():
	instance_cursor = instances.find({})
	thread_list = []
	for document in instance_cursor:
		thread = threading.Thread(target=app_handler, args=(document,))
		thread_list.append(thread)
		thread.start()
	for thread in thread_list:
		thread.join()