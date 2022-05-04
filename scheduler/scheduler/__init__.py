from flask import Flask
import kafka
from pymongo import MongoClient
import gridfs
import json
import importlib.resources as pkg_resources
from scheduler.kafka import KafkaAdmin

app = Flask(__name__)
module_config = json.loads(
    pkg_resources.read_binary('scheduler', 'config.json'))

kafka_server = "{}:{}".format(module_config['kafka_ip'], module_config['kafka_port'])
messenger = KafkaAdmin(kafka_server, 'scheduler')

client = MongoClient(module_config['mongo_server'])
db = client.repo
