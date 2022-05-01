import ast
from flask import Flask, jsonify, Response, request
import json
import pymongo
import logging
import threading
import requests
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
controller_config = db["controllerdetails"]
logging.info("Sensor database created")

app = Flask(__name__)

buffer=dict()

def db_change_detector():
    for change in sensor_config.watch():
        change_type = change['operationType']
        if change_type == "insert":
            document_id = change['documentKey']
            document = sensor_config.find_one(document_id)
            topic=document["topic_id"]
            sensorThread(topic,buffer)

class thread(threading.Thread):
    def __init__(self,topic,buffer):
        threading.Thread.__init__(self)
        self.topic=topic
        self.buffer=buffer
    def run(self):
        consumer = KafkaConsumer(self.topic, bootstrap_servers=[kafka_server], enable_auto_commit=True)
        for msg in consumer:
            buffer[self.topic]=msg.value

def sensorThread(topic,buffer):
    logging.info('Starting consumer')
    thread1 = thread(topic,buffer)
    thread1.start()

def start_pending_threads():
    sensors_cursor = sensor_config.find({})
    for document in sensors_cursor:
        topic=document["topic_id"]
        sensorThread(topic,buffer)

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

@app.route("/controller/<controller_id>", methods=["GET", "POST"])
def send_to_controller(controller_id):
    controller = controller_config.find_one({'controller_id': controller_id })
    url = "http://{}:{}/".format(controller["IP"], controller["PORT"])
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

@app.route("/data/<sensor_id>")
def getSensorData(sensor_id):
    logging.info("Connected to kafka")
    data=buffer[sensor_id]
    logging.info(type(data))
    return data
