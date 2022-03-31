from sensor_manager.server import app, producer, sensor_config
from sensor_manager.sensorManager import start_all_threads

if __name__ == "__main__":
<<<<<<< HEAD
	start_all_threads(producer, sensor_config)
	app.run()
=======
	module_config = json.loads(pkg_resources.read_binary('sensor_manager', 'config.json'))
	run(module_config['kafka_ip'], module_config['kafka_port'], module_config['mongo_server'])
>>>>>>> 61a3868799b63c3b091f4dc1843fac7c52fa8102
