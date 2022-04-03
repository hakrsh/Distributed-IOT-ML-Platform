import ast
from flask import Flask, jsonify
import json
import pymongo
import logging
import threading
from kafka import KafkaConsumer
from sensor_request_handler.config import module_config

logging.basicConfig(level=logging.INFO)

kafka_ip = module_config["kafka_ip"]
kafka_port = module_config["kafka_port"]

kafka_server = "{}:{}".format(kafka_ip, kafka_port)
mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info("Connected to database")

db = client["sensors"]
sensor_config = db["sensordetails"]
logging.info("Sensor database created")

app = Flask(__name__)

###############################02-04-2022############################################start
class thread(threading.Thread):
    def __init__(self,topic,buffer):
        threading.Thread.__init__(self)
        self.topic=topic
        self.buffer=buffer
    def run(self):
        consumer = KafkaConsumer(self.topic, bootstrap_servers=[kafka_server], enable_auto_commit=True)
        for msg in consumer:
            buffer[self.topic]=ast.literal_eval(msg.value.decode("utf-8"))

def sensorThread(topic,buffer):
    logging.info('Starting consumer')
    thread1 = thread(topic,buffer)
    thread1.start()

buffer=dict()
def sensor():
    sensors_cursor = sensor_config.find({})
    for document in sensors_cursor:
        topic=document["topic_id"]
        sensorThread(topic,buffer)
sensor()
###############################02-04-2022############################################end

@app.route("/getAllSensors")
def getAllSensors():
    sensors_cursor = sensor_config.find({})
    list_of_sensors = []
    for document in sensors_cursor:
        sensorinfo = {}
        sensorinfo["sensor_id"] = document["topic_id"]
        sensorinfo["sensor_type"] = document["Type"]
        sensorinfo["sensor_location"] = document["Location"]
        list_of_sensors.append(sensorinfo)
    return jsonify(list_of_sensors)


@app.route("/data/<sensor_id>")
def getSensorData(sensor_id):
    logging.info("Connected to kafka")
    data=buffer[sensor_id]
    return jsonify(data)
