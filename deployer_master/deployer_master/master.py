from http import client
from flask import Flask, request
from pymongo import MongoClient
import requests
import logging
import uuid

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
client = MongoClient('mongodb+srv://root:root@ias.tu9ec.mongodb.net/repo?retryWrites=true&w=majority')
db = client.repo

@app.route('/')
def index():
    return 'Deployer Master is running'

@app.route('/model', methods=['POST'])
def deploy_model():
    model_id = request.json['ModelId']
    logging.info('ModelID: ' + model_id)
    instance_id = str(uuid.uuid4())
    logging.info("InstanceID: " + instance_id)
    db.instances.insert_one({"instance_id": instance_id, "type": "model",
                            "model_id": model_id, "status": "pending"})
    logging.info("Created deployment record")
    res = requests.post('http://localhost:9898/model', json={'ModelId': model_id, 'InstanceId': instance_id})
    logging.info("Sent request to model service")
    return res.text

@app.route('/app', methods=['POST'])
def deploy_app():
    application_id = request.json['ApplicationID']
    sensor_ids = request.json['sensor_ids']
    logging.info("ApplicationID: " + application_id)
    instance_id = str(uuid.uuid4())
    logging.info("InstanceID: " + instance_id)
    db.instances.insert_one({"instance_id": instance_id, "type": "app",
                            "model_id": application_id, "status": "pending"})
    logging.info("Created deployment record")
    res = requests.post('http://localhost:9898/app', json={'ApplicationID': application_id, 'InstanceId': instance_id, 'sensor_ids': sensor_ids})
    logging.info("Sent request to app service")
    return res.text
    
@app.route('/deployed', methods=['POST'])
def update_deployed_status():
    instance_id = request.json['InstanceId']
    res = request.json['res']
    # update instance status
    db.instances.update_one({"instance_id": instance_id}, {"$set": {
                            "status": res['container_status'],
                            "container_id": res['container_id'],
                            "hostname": res['host_name'],
                            "ip": res['host_ip'],
                            "port": res['port']}})
    logging.info('Updated instance db status')
    return {"Status": "success"}

@app.route('/stopped', methods=['POST'])
def update_stopped_status():
    instance_id = request.json['InstanceId']
    res = request.json['res']
    # update instance status
    db.instances.update_one({"instance_id": instance_id}, {"$set": {
                            "status": res['container_status'],}})
    logging.info('Updated instance db status')
    return {"Status": "success"}

@app.route('/stop-instance', methods=['POST'])
def stopInstance():
    instance_id = request.json['InstanceID']
    logging.info("InstanceID: " + instance_id)
    instance = db.instances.find_one({"instance_id": instance_id})
    if instance is None:
        return {"InstanceID": instance_id, "Status": "not found"}
    if instance['status'] != 'running':
        return {"InstanceID": instance_id, "Status": "not running"}
    res = requests.post('http://localhost:9898/stop-instance', json={'InstanceID': instance_id, 'ContainerID': instance['container_id']})
    return {"InstanceID": instance_id, "Status": "stopped"}

if __name__ == '__main__':
    app.run(port=9999, host='0.0.0.0')