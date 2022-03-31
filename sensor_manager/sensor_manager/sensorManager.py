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
    thread1 = thread(topic_id,ip,port,qf, producer)
    thread1.start()

def start_all_threads(producer, sensor_config):
    sensors_cursor = sensor_config.find({})
    for document in sensors_cursor:
        logging.info("Starting thread for {}".format(document['topic_id']))
        # thread1 = thread(document['topic_id'], document['IP'], document['PORT'], document['QueryFrequency'], producer)
        # thread1.start()
        producerStart(document['IP'], document['PORT'] , document['QueryFrequency'], document['topic_id'], producer)
