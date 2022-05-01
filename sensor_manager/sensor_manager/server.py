from flask import Flask, render_template, request
from sensor_manager.config import module_config
from sensor_manager.sensorManager import producerStart, start_all_threads
from kafka import KafkaProducer
import logging
import pymongo
import time
import socket

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
sensor_type_config = db["sensortype"]
controller_config = db["controllerdetails"]
controller_type_config = db["controllertype"]
logging.info('Sensor database created')

app = Flask(__name__)

def check_socket(conn_ip, conn_port):
	print("Checking", flush=True)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.settimeout(1)
	print("Sock estabilished", flush=True)
	result = sock.connect_ex((conn_ip,int(conn_port)))
	print("Connected", flush=True)
	if result == 0:
		sock.close()
		return True
	else:
		sock.close()
		return False	

@app.route('/')
def home():
	return render_template('sensor_home.html')

@app.route('/register_sensor')
def sensor_instance_home():
	types = sensor_type_config.distinct('type')
	return render_template('register_sensor.html', types=types)

@app.route('/register_controller')
def controller_instance_home():
	types = controller_type_config.distinct('type')
	return render_template('register_controller.html', types=types)

@app.route('/register_sensor_type')
def sensor_type_home():
	return render_template('register_sensor_type.html')

@app.route('/register_controller_type')
def controller_type_home():
	return render_template('register_controller_type.html')

@app.route('/register_stype', methods=['POST'])
def register_stype():
	s_type = request.form['type']
	if sensor_type_config.find({'type':s_type}).count() > 0:
		return "Type already exists!"
	sensor_type_config.insert_one({"type":s_type})
	return "Sensor type registered successfully!"

@app.route('/register_ctype', methods=['POST'])
def register_ctype():
	c_type = request.form['type']
	if controller_type_config.find({'type':c_type}).count() > 0:
		return "Type already exists!"
	controller_type_config.insert_one({"type":c_type})
	return "Controller type registered successfully!"

@app.route('/register_s', methods=['POST'])
def register_sensor():
	s_type = request.form['type']
	ip = request.form['ip']
	port = request.form['port']
	qf = int(request.form['qf'])
	loc = request.form['loc']
	topic_id = "{}{}".format(ip, port).replace('.','')
	print(request.form, flush=True)
	if not check_socket(ip, port):
		return "Sensor instance not reachable"
	print("Check done", flush=True)
	if sensor_config.find({'topic_id':topic_id}).count() > 0:
		return "Sensor instance already exists!"
	data_dict = dict() 
	data_dict["Type"] = s_type
	data_dict["IP"] = ip
	data_dict["PORT"] = port
	data_dict["QueryFrequency"] = qf
	data_dict["Location"] = loc
	data_dict["topic_id"] = topic_id
	print("Reached 1", flush=True)
	sensor_config.insert_one(data_dict)
	print("Reached 2", flush=True)
	producerStart(ip, port,qf, topic_id, producer)
	return "Sensor instance registered successfully!"

@app.route('/register_c', methods=['POST'])
def register_controller():
	c_type = request.form['type']
	ip = request.form['ip']
	port = request.form['port']
	loc = request.form['loc']
	if not check_socket(ip, port):
		return "Controller instance not reachable"
	if controller_config.find({'IP':ip, 'PORT':port}).count() > 0:
		return "Controller instance already exists!"
	controller_id = "{}{}".format(ip, port).replace('.','')
	data_dict = dict() 
	data_dict["Type"] = c_type
	data_dict["IP"] = ip
	data_dict["PORT"] = port
	data_dict["Location"] = loc
	data_dict["controller_id"] = controller_id
	controller_config.insert_one(data_dict)
	return "Controller instance registered successfully!"