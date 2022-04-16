from flask import Flask
from deployer_master.kafka import KafkaAdmin
from pymongo import MongoClient
import json
import importlib.resources as pkg_resources


app = Flask(__name__)
module_config = json.loads(
    pkg_resources.read_binary('deployer_master', 'config.json'))

kafka_server = "{}:{}".format(module_config['kafka_ip'], module_config['kafka_port'])
messenger = KafkaAdmin(kafka_server, 'platform_manager')
client = MongoClient(module_config['mongo_server'])
db = client.repo
