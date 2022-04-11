from flask import Flask
from pymongo import MongoClient
import json
import importlib.resources as pkg_resources


app = Flask(__name__)
models = json.loads(pkg_resources.read_text(__name__, 'models.json'))
module_config = json.loads(
    pkg_resources.read_binary('model_request_handler', 'config.json'))


# kafka_server = "{}:{}".format(module_config['kafka_ip'], module_config['kafka_port'])
# mongo_server = "{}:{}".format(
#     module_config['mongo_ip'], module_config['mongo_port'])

client = MongoClient(module_config['mongo_server'])
db = client.repo
