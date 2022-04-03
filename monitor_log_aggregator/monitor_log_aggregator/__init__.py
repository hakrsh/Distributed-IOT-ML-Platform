import json
import importlib.resources as pkg_resources
from pymongo import MongoClient

module_config = json.loads(
    pkg_resources.read_binary('monitor_log_aggregator', 'config.json'))


kafka_server = "{}:{}".format(module_config['kafka_ip'], module_config['kafka_port'])

client = MongoClient(module_config['mongo_server'])
db_instances = client.repo
db_topics = client.logger