from flask import Flask
import json
import pymongo
import logging
from kafka import KafkaConsumer
from sensor_request_handler.config import module_config

logging.basicConfig(level=logging.INFO)

kafka_ip = module_config['kafka_ip']
kafka_port = module_config['kafka_port']

kafka_server = "{}:{}".format(kafka_ip, kafka_port)
mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

db = client[ "sensors" ]
sensor_config = db["sensordetails"]
logging.info('Sensor database created')

app = Flask(__name__)

@app.route("/getAllSensors")
def getAllSensors():
	sensors_cursor = sensor_config.find({})
	list_of_sensors = []
	for document in sensors_cursor:
			sensorinfo = {}
			sensorinfo["sensor_id"] = document['topic_id']
			sensorinfo["sensor_type"] = document['Type']
			sensorinfo["sensor_location"] = document['Location']
			list_of_sensors.append(sensorinfo)
	return str(list_of_sensors)


@app.route("/data/<sensor_id>")
def getSensorData(sensor_id):
    print(sensor_id)
    consumer = KafkaConsumer(sensor_id, bootstrap_servers=[kafka_server], enable_auto_commit=True)
    logging.info("Connected to kafka")
    data = []
    for message in consumer:
        print(message.value.decode('utf-8'))
        data.append(message.value.decode('utf-8'))
        break
    return str(data)
