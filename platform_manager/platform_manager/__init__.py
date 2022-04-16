from flask import Flask
import kafka
from pymongo import MongoClient
import gridfs
import json
import importlib.resources as pkg_resources
from platform_manager.kafka import KafkaAdmin

app = Flask(__name__)
module_config = json.loads(
    pkg_resources.read_binary('platform_manager', 'config.json'))

kafka_server = "{}:{}".format(module_config['kafka_ip'], module_config['kafka_port'])
messenger = KafkaAdmin(kafka_server, 'platform_manager')

client = MongoClient(module_config['mongo_server'])
fs = gridfs.GridFS(client.fs)
db = client.repo
