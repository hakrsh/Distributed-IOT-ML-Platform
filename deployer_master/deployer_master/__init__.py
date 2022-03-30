from flask import Flask
from pymongo import MongoClient
import json
import importlib.resources as pkg_resources


app = Flask(__name__)
module_config = json.loads(
    pkg_resources.read_binary('deployer-master', 'config.json'))

client = MongoClient(module_config['mongo_server'])
db = client.repo
