import json
from sensor_manager.sensorManager import run
import importlib.resources as pkg_resources

if __name__ == "__main__":
	module_config = json.loads(pkg_resources.read_binary('sensor_manager', 'config.json'))
	run(module_config['kafka_ip'], module_config['kafka_port'], module_config['mongo_ip'], module_config['mongo_port'])