from monitor_ha.config import module_config
import pymongo
import logging
import threading
import time
import docker
import requests
import json
from kafka import KafkaProducer
from paramiko import SSHException

logging.basicConfig(level=logging.INFO)

monitor_interval = 5

mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

kafka_ip = module_config['kafka_ip']
kafka_port = module_config['kafka_port']

kafka_server = "{}:{}".format(kafka_ip, kafka_port)
mongo_server = module_config["mongo_server"]

producer = KafkaProducer(bootstrap_servers=[kafka_server],api_version=(0,10,1), value_serializer=lambda v: json.dumps(v).encode('utf-8'))
logging.info('Connected to kafka')

deployer_topic = "to_deployer_master"

db = client[ "repo" ]
instances = db["instances"]
logging.info('instance database created')

thread_list = []

def connect_cleanup_container(hostname, ip, container_id):
	logging.info("Starting cleanup thread for {} in {}".format(container_id, hostname))
	while True:
		try:
			client = docker.DockerClient(base_url="ssh://{}@{}".format(hostname, ip))
		except Exception as e:
			logging.error("Could not connect to docker daemon, retrying")
			logging.info("Vm cleanup thread retrying connection to docker client")

def cleanup(hostname, ip, container_id, instance_id):
	logging.info("Cleaning up {}".format(container_id))
	instances.delete_one({"instance_id":instance_id})
	logging.info("Removing container from worker")
	global thread_list
	thread = threading.Thread(target=connect_cleanup_container, args=(hostname, ip, container_id,))
	thread_list.append(thread)

def recover(itype, app_info, instance_id):
	if itype == "model":
		logging.info('Sending model to deployer')
		producer.send(deployer_topic, {"type":"model", "ModelId": app_info["model_id"],"model_name":app_info["model_name"]})
	else:
		query = {
			"type":"app",
			"ApplicationID":app_info["application_id"],
			"app_name":app_info["app_name"],
			"sensor_ids":app_info["sensor_ids"],
			"sched_id":app_info["sched_id"]
		}
		logging.info('Sending app to deployer')
		producer.send(deployer_topic, query)

def handler(app_info):
	instance_id = app_info["instance_id"]
	hostname = app_info["hostname"]
	ip = app_info["ip"]
	port = app_info["port"]
	itype = app_info["type"]	
	container_id = app_info["container_id"]
	logging.info(ip)
	logging.info(port)
	retry_count = 0
	while True:
		try:
			client = docker.DockerClient(base_url="ssh://{}@{}".format(hostname, ip))
			break
		except Exception as e:
			retry_count += 1
			if retry_count == 5:
				logging.info("Container {} not running".format(container_id))
				cleanup(hostname, ip, container_id, instance_id)
				logging.info("Recovering {}".format(container_id))
				recover(itype, app_info, instance_id)
				logging.info("Recovery done!")
			logging.error("Could not connect to docker daemon")
			logging.info("Init thread, Retrying connection to docker client")
	logging.info("Connected to daemon for {}, Starting monitoring".format(container_id))
	while True:
		try:
			cont = client.containers.get(container_id)
			cont_status = cont.status
			logging.info("{} {} {}".format(itype, container_id, cont_status))
			if cont_status == "exited":
				logging.info("Container {} not running".format(container_id))
				cleanup(hostname, ip, container_id, instance_id)
				logging.info("Recovering {}".format(container_id))
				recover(itype, app_info, instance_id)
				logging.info("Recovery done!")
		except SSHException:
				logging.info("Host unreachable for {}, rescheduling".format(container_id))
				cleanup(hostname, ip, container_id, instance_id)
				logging.info("Recovering {}".format(container_id))
				recover(itype, app_info, instance_id)
				logging.info("Recovery done!")
		except Exception as e:
			logging.error(e)
		document = db.instances.find_one({"instance_id": instance_id})
		if document == None:
			logging.info("Stopping monitoring for {}".format(container_id))
			break
		time.sleep(monitor_interval)
	logging.info("Exiting thread")

def run():
	global thread_list

	# instance_cursor = instances.find({})
	# for document in instance_cursor:
	# 	if document["status"] != "init" or document["status"] != "pending":
	# 		logging.info("Starting thread for {}".format(document))
	# 		thread = threading.Thread(target=handler, args=(document,))
	# 		thread_list.append(thread)
	# 		thread.start()

	for change in instances.watch():
		change_type = change['operationType']
		logging.info(change)
		if change_type == "update":
			logging.info("Starting thread")
			document_id = change['documentKey']
			document = instances.find_one(document_id)
			if document["status"] == "running":
				thread = threading.Thread(target=handler, args=(document,))
				thread_list.append(thread)
				thread.start()

	for thread in thread_list:
		thread.join()