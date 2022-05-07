import threading
import requests
import json
from kafka import KafkaConsumer
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')

logging.info('Loading sensor config')
controller_config = json.loads(open('controller_config.json').read())
if controller_config['controller_id'] == '':
    logging.info('Generating sensor id')
    controller_config['controller_id'] = str(uuid.uuid4())[:8]
    with open('controller_config.json', 'w') as f:
        f.write(json.dumps(controller_config))

def send_sms(phone,msg):
    url = "https://www.fast2sms.com/dev/bulk"
    headers = {
    'authorization': "Aeoh3MDGpWajkNVBxmSysJgOKzIf7LPTc2YUw6tiR9lZEbv10Q8EX5xvCAYP31kMTDQmStB9s46l7nJq",
    'Content-Type': "application/x-www-form-urlencoded",
    'Cache-Control': "no-cache",
    }
    payload = "sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers="+phone
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

consumer = KafkaConsumer(controller_config['controller_id'], group_id=controller_config['controller_id'], bootstrap_servers=controller_config['kafka_server'], auto_offset_reset='earliest', enable_auto_commit=True)

while True:
    logging.info('Waiting for message')
    for message in consumer:
        logging.info('Received message')
        message = json.loads(message.value.decode('utf-8'))
        threading.Thread(target=send_sms, args=(message['phone'],message['msg'])).start()
        logging.info('Sent message')


