from flask import Flask, render_template, request
from itsdangerous import json
from sensor_manager.config import module_config
import logging
import pymongo
import importlib.resources as pkg_resources
from jsonschema import validate


logging.basicConfig(level=logging.INFO)

mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

db = client[ "sensors" ]
sensor_details = db["sensordetails"]
sensor_type_config = db["sensortype"]
controller_details = db["controllerdetails"]
controller_type_config = db["controllertype"]
logging.info('Sensor database created')

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('sensor_home.html')

@app.route('/register_sensor')
def sensor_instance_home():
	return render_template('register_sensor.html')

@app.route('/register_controller')
def controller_instance_home():
	return render_template('register_controller.html')

@app.route('/register_s', methods=['POST'])
def register_sensor():
	sensor_config = json.loads(request.files['sensor_config'].read())
	schema = json.loads(pkg_resources.read_text('sensor_manager', 'sensor_schema.json'))
	try:
		validate(sensor_config, schema)
	except Exception as e:
		return 'Invalid sensor configuration: {}'.format(e)
	topic_id = sensor_config['topic_id']
	name = sensor_config['Name']
	if sensor_details.find({'topic_id':topic_id}).count() > 0:
		return "Sensor instance already exists!"
	if sensor_details.find({'name':name}).count() > 0:
		return "Sensor name already exists!"
	s_type = sensor_config['Type']
	if sensor_type_config.find({'type':s_type}).count() == 0:
		sensor_type_config.insert_one({"type":s_type})
	sensor_details.insert_one(sensor_config)
	return "Sensor instance registered successfully!"

@app.route('/register_c', methods=['POST'])
def register_controller():
	controller_config = json.loads(request.files['controller_config'].read())
	schema = json.loads(pkg_resources.read_text('sensor_manager', 'controller_schema.json'))
	try:
		validate(controller_config, schema)
	except Exception as e:
		return 'Invalid controller configuration: {}'.format(e)
	controller_id = controller_config['controller_id']
	name = controller_config['Name']
	if controller_details.find({'controller_id':controller_id}).count() > 0:
		return "Controller instance already exists!"
	if controller_details.find({'name':name}).count() > 0:
		return "Controller name already exists!"
	c_type = controller_config['Type']
	if controller_type_config.find({'type':c_type}).count() == 0:
		controller_type_config.insert_one({"type":c_type})
	controller_details.insert_one(controller_config)
	return "Controller instance registered successfully!"
