from flask import Flask, render_template, request
from sensor_manager.config import module_config
from sensor_manager.sensorManager import producerStart, start_all_threads
from kafka import KafkaProducer
import logging
import pymongo
import time

logging.basicConfig(level=logging.INFO)

kafka_ip = module_config['kafka_ip']
kafka_port = module_config['kafka_port']

kafka_server = "{}:{}".format(kafka_ip, kafka_port)
mongo_server = module_config["mongo_server"]

producer = KafkaProducer(bootstrap_servers=[kafka_server],api_version=(0,10,1))
logging.info('Connected to kafka')

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

db = client[ "sensors" ]
sensor_config = db["sensordetails"]
logging.info('Sensor database created')

app = Flask(__name__)

@app.route('/register')
def home():
    return render_template('register.html')

@app.route('/register_sensor', methods=['POST'])
def register():
	s_type = request.form['type']
	ip = request.form['ip']
	port = request.form['port']
	qf = int(request.form['qf'])
	loc = request.form['loc']
	topic_id = "{}{}".format(ip, port).replace('.','')
	if sensor_config.find({'topic_id':topic_id}).count() > 0:
		return "Sensor already exists!"
	data_dict = dict() 
	data_dict["Type"] = s_type
	data_dict["IP"] = ip
	data_dict["PORT"] = port
	data_dict["QueryFrequency"] = qf
	data_dict["Location"] = loc
	data_dict["topic_id"] = topic_id
	sensor_config.insert_one(data_dict)
	producerStart(ip, port,qf, topic_id, producer)
	return "Sensor registered successfully!"