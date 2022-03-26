import json
import pymongo
from kafka.admin import KafkaAdminClient, NewTopic
import threading
from time import sleep
from kafka import KafkaProducer
import requests
import logging
import importlib.resources as pkg_resources


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
            sleep(self.frequency)

    
def createKafkaTopic(kafka_server, numberOfThread):
    logging.info('Creating kafka topic')
    admin_client = KafkaAdminClient(bootstrap_servers=kafka_server)
    topic_list = list()
    for id in range(int(numberOfThread)):
        topic_list.append(NewTopic(name=str(id), num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
 

def producerStart(numberOfThread, sensor_config, producer):
    logging.info('Starting producer')
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