from flask import Flask
from pymongo import MongoClient
import gridfs
import json
import importlib.resources as pkg_resources

app = Flask(__name__)
module_config = json.loads(
    pkg_resources.read_binary('deployer', 'config.json'))

kafka_server = "{}:{}".format(module_config['kafka_ip'], module_config['kafka_port'])
client = MongoClient(module_config['mongo_server'])
fs = gridfs.GridFS(client.fs)
db = client.repo
