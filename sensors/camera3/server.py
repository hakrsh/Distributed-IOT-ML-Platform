import random
import time
import cv2
import os
from kafka import KafkaProducer
from io import BytesIO
import logging
import json
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
images = os.listdir('images')

logging.info('Loading sensor config')
sensor_config = json.loads(open('sensor_config.json').read())
if sensor_config['topic_id'] == '':
    logging.info('Generating sensor id')
    sensor_config['topic_id'] = str(uuid.uuid4())[:8]
    with open('sensor_config.json', 'w') as f:
        f.write(json.dumps(sensor_config))

producer = KafkaProducer(bootstrap_servers=sensor_config['kafka_server'])

def gen_frame():
    index = random.randint(0, len(images)-1)
    file = images[index]
    frame = cv2.imread("images/{}".format(file))
    ret, buffer = cv2.imencode('.jpg', frame)
    data = buffer.tobytes()
    return data

while True:
    data = BytesIO(gen_frame())
    producer.send(sensor_config['topic_id'], data.getvalue())
    logging.info('Produced data to topic: {}'.format(sensor_config['topic_id']))
    time.sleep(sensor_config['query_frequency'])