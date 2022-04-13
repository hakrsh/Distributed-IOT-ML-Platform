from monitor_ha.config import module_config
import pymongo
import logging
import threading
import time
import docker
import requests

logging.basicConfig(level=logging.INFO)

monitor_interval = 5

mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

db = client[ "repo" ]
instances = db["instances"]
logging.info('instance database created')

def app_handler(app_info):
	instance_id = app_info["instance_id"]
	hostname = app_info["hostname"]
	ip = app_info["ip"]
	port = app_info["port"]
	itype = app_info["type"]	
	container_id = app_info["container_id"]
	try:
		client = docker.DockerClient(base_url="ssh://{}@{}".format(hostname, ip))
	except Exception as e:
		logging.error("Could not connect to docker daemon")
	while True:
		try:
			cont = client.containers.get(container_id)
			cont_status = cont.status
			logging.info("Container {} {}".format(container_id, cont_status))
			if cont_status != "running":
				logging.info("Container {} not running".format(container_id))
				logging.info("Cleaning up {}".format(container_id))
				instances.delete_one({"instance_id":instance_id})
				logging.info("Removing container from worker")
				cont.remove()
				logging.info("Recovering {}".format(container_id))
				if itype == "model":
					url = module_config['deployer_master'] + '/model'
					logging.info('Sending model to deployer')
					response = requests.post(url, json={"ModelId": app_info["model_id"],"model_name":app_info["model_name"]}).content
					print(response)
				else:
					scheduler_endpoint = module_config["scheduler_endpoint"]
					reschedule_api = "{}/reschedule/{}".format(scheduler_endpoint, instance_id)
					response = requests.get(reschedule_api)
				logging.info("Recovery done!")
		except Exception as e:
			logging.info("Container {} not running".format(container_id))
			instances.delete_one({"instance_id":instance_id})
			logging.info("Recovering {}".format(container_id))
			if itype == "model":
				url = module_config['deployer_master'] + '/model'
				logging.info('Sending model to deployer')
				response = requests.post(url, json={"ModelId": app_info["model_id"],"model_name":app_info["model_name"]}).content
				print(response)
			else:
				scheduler_endpoint = module_config["scheduler_endpoint"]
				reschedule_api = "{}/reschedule/{}".format(scheduler_endpoint, instance_id)
				response = requests.get(reschedule_api)
			logging.info("Recovery done!")
		document = db.instances.find_one({"instance_id": instance_id})
		if document == None:
			break
		time.sleep(monitor_interval)
	logging.info("Exiting thread")

def run():
	instance_cursor = instances.find({})
	thread_list = []
	for document in instance_cursor:
		thread = threading.Thread(target=app_handler, args=(document,))
		thread_list.append(thread)
		thread.start()

	for change in instances.watch():
		change_type = change['operationType']
		logging.info(change)
		if change_type == "update":
			logging.info("Starting thread")
			document_id = change['documentKey']
			document = instances.find_one(document_id)
			thread = threading.Thread(target=app_handler, args=(document,))
			thread_list.append(thread)
			thread.start()

	for thread in thread_list:
		thread.join()
