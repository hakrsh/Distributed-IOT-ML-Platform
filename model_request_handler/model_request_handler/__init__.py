from flask import Flask
from pymongo import MongoClient
import json
import importlib.resources as pkg_resources
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

module_config = json.loads(
    pkg_resources.read_binary('model_request_handler', 'config.json'))

client = MongoClient(module_config['mongo_server'])
db = client.repo
if len(list(db.model_map.find())) != 0:
    logging.info('Restoring model_map from db')
    models = db.model_map.find_one()
else:
    logging.info('Creating model_map')
    models = {}
