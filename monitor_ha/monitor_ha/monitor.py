from monitor_ha.config import module_config
import pymongo
import logging
import threading
import time
import docker
import requests

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
	instances.delete_one({"instance_id":instance_id})
	client.remove(container_id)

def recover(instance_id):
	logging.info("Recovering {}".format(container_id))
	scheduler_endpoint = module_config["scheduler_endpoint"]
	reschedule_api = "{}/reschedule/{}".format(scheduler_endpoint, instance_id)
	response = requests.get(reschedule_api)
	return response

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
		document = db.instances.find_one({"instance_id": instance_id})
		if document == None:
			break
		logging.info("Running")
		time.sleep(monitor_interval)

def run():
	instance_cursor = instances.find({})
	thread_list = []
	for document in instance_cursor:
		thread = threading.Thread(target=app_handler, args=(document,))
		thread_list.append(thread)
		thread.start()

	for change in instances.watch():
		change_type = change['operationType']
		document_id = change['documentKey']
		document = instances.find_one(document_id)
		thread = threading.Thread(target=app_handler, args=(document,))
		thread_list.append(thread)

	for thread in thread_list:
		thread.join()
