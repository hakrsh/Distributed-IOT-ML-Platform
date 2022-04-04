from flask import Flask
from pymongo import MongoClient
import json
import importlib.resources as pkg_resources


app = Flask(__name__, static_url_path='', static_folder='templates/static', template_folder='templates')
module_config = json.loads(
    pkg_resources.read_binary('auth', 'config.json'))


client = MongoClient(module_config['mongo_server'])
db = client.users
