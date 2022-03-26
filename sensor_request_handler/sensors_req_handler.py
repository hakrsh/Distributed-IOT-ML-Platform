from flask import Flask, jsonify
from flask_pymongo import PyMongo
import json
import ast

from kafka import KafkaConsumer


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://root:root@ias.tu9ec.mongodb.net/sensors?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route("/getAllSensors")
def getAllSensors():
	sensors_cursor = mongo.db.sensordetails.find()
	list_of_sensors = []
	for cursor in sensors_cursor:
		# for key in cursor:
		# 	print(type(cursor[key]))
		# 	if type(cursor[key]) is dict:
		# 		print(cursor[key])
		# 		sensorinfo = {}
		# 		sensorinfo["sensor_id"] = key
		# 		sensorinfo["sensor_type"] = cursor[key]["Type"]
		# 		sensorinfo["sensor_location"] = cursor[key]["Location"]
		# 		list_of_sensors.append(sensorinfo)
		sensorinfo = {}
		sensorinfo["sensor_id"] = cursor["_id"]
		sensorinfo["sensor_type"] = cursor["value"]["Type"]
		sensorinfo["sensor_location"] = cursor["value"]["Location"]
		list_of_sensors.append(sensorinfo)

	return jsonify(list_of_sensors)


@app.route("/data/<sensor_id>")
def getSensorData(sensor_id):
    print(sensor_id)
    consumer = KafkaConsumer(sensor_id, bootstrap_servers=['20.232.42.212:9092'])
    data = ''
    for message in consumer:
        data = message.value.decode('utf-8')
        return ast.literal_eval(data)
        
	# return data
    

if __name__ == "__main__":
	app.run(port=7000,debug=True,host='0.0.0.0')
	
