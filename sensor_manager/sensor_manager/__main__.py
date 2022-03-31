from sensor_manager.server import app, producer, sensor_config
from sensor_manager.sensorManager import start_all_threads

if __name__ == "__main__":
	start_all_threads(producer, sensor_config)
	app.run(port=7005,host='0.0.0.0')
