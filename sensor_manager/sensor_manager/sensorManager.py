import json
import pymongo
from flask import Flask
import threading
from time import sleep
import requests
import logging
import urllib3

logging.basicConfig(level=logging.INFO)

class thread(threading.Thread):
    def __init__(self, topic_id, ip, port, frequency, producer):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.frequency = frequency
        self.topic_id = topic_id
        self.producer = producer

    def run(self):
        while(True):
            url = "http://"+self.ip+":"+self.port+"/"
            response = requests.get(url=url)
            res = bytes(response.text, 'utf-8')
            self.producer.send(str(self.topic_id),res)
            logging.info(str(threading.current_thread().ident))
            logging.info("Pushed value for {}".format(self.topic_id))
            sleep(self.frequency)

def producerStart(ip, port, qf, topic_id, producer):
    logging.info('Starting producer')
<<<<<<< HEAD
    thread1 = thread(topic_id,ip,port,qf, producer)
    thread1.start()

def start_all_threads(producer, sensor_config):
    sensors_cursor = sensor_config.find({})
    for document in sensors_cursor:
        logging.info("Starting thread for {}".format(document['topic_id']))
        # thread1 = thread(document['topic_id'], document['IP'], document['PORT'], document['QueryFrequency'], producer)
        # thread1.start()
        producerStart(document['IP'], document['PORT'] , document['QueryFrequency'], document['topic_id'], producer)
=======
    for topic_id in range(int(numberOfThread)):
        document = sensor_config.find_one({"_id":topic_id})
        thread1 = thread(topic_id,document['value']['IP'],document['value']['PORT'],document['value']['QueryFrequency'], producer)
        thread1.start()


def run(kafka_ip, kafka_port, mongo_server):
    kafka_server = "{}:{}".format(kafka_ip, kafka_port)
    # mongo_server = "{}:{}".format(mongo_ip, mongo_port)

    producer = KafkaProducer(bootstrap_servers=[kafka_server],api_version=(0,10,1))
    logging.info('Connected to kafka')

    client = pymongo.MongoClient(mongo_server)
    logging.info('Connected to database')

    db = client[ "sensors" ]
    sensor_config = db["sensordetails"]
    sensor_config.delete_many({})
    logging.info('Sensor database created')

    sensorJson = pkg_resources.read_binary('sensor_manager', 'sensorConfig.json')
    sensorData = json.loads(sensorJson)

    numberOfThread = len(sensorData["Sensors"])

    for key,item in enumerate(sensorData["Sensors"]):
        record={"_id":key,"value":item}
        sensor_config. insert_one(record)
    #createKafkaTopic(numberOfThread)
    producerStart(numberOfThread, sensor_config, producer)
>>>>>>> 61a3868799b63c3b091f4dc1843fac7c52fa8102
