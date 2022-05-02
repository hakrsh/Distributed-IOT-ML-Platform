import threading
from time import sleep
import requests
import logging

from io import BytesIO

from io import BytesIO

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
        count = 0
        while(True):
            url = "http://"+self.ip+":"+self.port+"/"
            response = requests.get(url=url)

            stream = BytesIO(response.content)

            self.producer.send(str(self.topic_id), stream.getvalue())
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
        producerStart(document['IP'], document['PORT'] , document['QueryFrequency'], document['topic_id'], producer)
