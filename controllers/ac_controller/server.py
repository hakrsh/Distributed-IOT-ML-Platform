import threading
import random
import time
import json
from flask import Flask, render_template, request
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

app = Flask(__name__)

state = 0

@app.route('/home')
def get_home():
	return render_template("index.html", state=state)

@app.route('/get_signal')
def get_data():
	global state
	return json.dumps(state)

@app.route('/',  methods = ['POST'])
def put_data():
	global state
	data = request.data
	state = int(json.loads(data)["signal"])
	return "Done!"

if __name__ == '__main__':
	app.run(port=7779, host='0.0.0.0')

