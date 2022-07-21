from flask import jsonify
import requests
import logging
import uuid
from deployer_master import app, db, module_config, kafka_server, messenger
import threading
import time 
import json
from kafka import KafkaConsumer


logging.basicConfig(level=logging.INFO)

def worker_status():
    for worker in module_config['workers']:
        try:
            if requests.get(f'http://{worker["ip"]}:9898').status_code == 200:
                time.sleep(5)
                return True
        except:
            continue
    return False

@app.route('/')
def index():
    return 'Deployer Master is running'

consumer = KafkaConsumer('to_deployer_master', bootstrap_servers=kafka_server, group_id='deployer', enable_auto_commit=True)

def deploy_model(message):
    logging.info("Deploying model " + str(message))
    model_id = message['ModelId']
    model_name = message['model_name']
    logging.info('ModelID: ' + model_id)
    instance_id = str(uuid.uuid4())[:8]
    logging.info("InstanceID: " + instance_id)
    db.instances.insert_one({"instance_id": instance_id,
                            "type": "model",
                             "model_id": model_id,
                             "model_name": model_name,
                             "status": "init",
                             "container_id": "",
                             "hostname": "",
                             "ip": "",
                             "port": ""})
    logging.info("Created deployment record")
    res = requests.post(f'{module_config["load_balancer"]}/model',
                        json={'ModelId': model_id, 'InstanceId': instance_id})
    logging.info("Sent request to model service")
    return res.text


def deploy_app(message):
    logging.info("Deploying app " + str(message))
    application_id = message['ApplicationID']
    app_name = message['app_name']
    sched_id = message['sched_id']
    sensor_ids = message['sensor_ids']
    controller_ids = message['controller_ids']
    logging.info("ApplicationID: " + application_id)
    instance_id = str(uuid.uuid4())[:8]
    logging.info("InstanceID: " + instance_id)
    db.instances.insert_one({"instance_id": instance_id,
                            "type": "app",
                             "model_id": application_id,
                             "app_name": app_name,
                             "application_id": application_id,
                             "sched_id": sched_id,
                             "sensor_ids": sensor_ids,
                             "controller_ids": controller_ids,
                             "status": "init",
                             "container_id": "",
                             "hostname": "",
                             "ip": "",
                             "port": ""})
    logging.info("Created deployment record")
    res = requests.post(f'{module_config["load_balancer"]}/app', json={
                        'ApplicationID': application_id,'app_name':app_name, 'InstanceId': instance_id, 'sensor_ids': sensor_ids,'sched_id':sched_id,'controller_ids':controller_ids})
    logging.info("Sent request to app service")
    messenger.send_message('from_deployer_master', res.text)
    return res.text

def stopInstance(message):
    logging.info("Stopping instance " + str(message))
    instance_id = message['instance_id']
    logging.info("InstanceID: " + instance_id)
    instance = db.instances.find_one({"instance_id": instance_id})
    if instance is None:
        return {"InstanceID": instance_id, "Status": "not found"}
    if instance['status'] != 'running':
        return {"InstanceID": instance_id, "Status": "not running"}
    ip = instance['ip']
    logging.info('Connecting to ' + ip)
    res = requests.post(f'http://{ip}:9898/stop-instance', json={
                        'InstanceID': instance_id, 'ContainerID': instance['container_id']})
    return res.text

def kafka_thread():
    logging.info("Inside kafka thread")
    while True:
        logging.info("Checking for new requests")
        for message in consumer:
            message = json.loads(message.value.decode('utf-8'))
            while worker_status() == False:
                logging.info("Waiting for workers to come online")
                time.sleep(2)
            if message['type'] == 'model':
                logging.info("New model deploy request")
                threading.Thread(target=deploy_model, args=(message,)).start()
            elif message['type'] == 'app':
                logging.info("Received app deploy request")
                threading.Thread(target=deploy_app, args=(message,)).start()
            elif message['type'] == 'stop':
                logging.info("Received stop instance request")
                threading.Thread(target=stopInstance, args=(message,)).start()            
        logging.info("No new model deployments")

def execute_pending():
    for instance in db.instances.find({"status": "init"}):
        while worker_status() == False:
            logging.info("Waiting for workers to come online")
            time.sleep(2)
        logging.info("Executing pending instance ")
        if instance['type'] == 'model':
            logging.info("Executing model instance")
            requests.post(f'{module_config["load_balancer"]}/model',
                        json={'ModelId': instance['model_id'], 'InstanceId': instance['instance_id']})
            logging.info("Sent request to model service")
        elif instance['type'] == 'app':
            logging.info("Executing app instance")
            requests.post(f'{module_config["load_balancer"]}/app', json={
                        'ApplicationID': instance['application_id'], 'InstanceId': instance['instance_id'], 'sensor_ids': instance['sensor_ids'],'sched_id':instance['sched_id'], 'controller_ids':instance['controller_ids']})
            logging.info("Sent request to app service")
    logging.info("Executed all pending instances")
        
def get_load_thread(worker):
    ip = worker['ip']
    logging.info('Connecting to ' + ip)
    res = requests.get(f'http://{ip}:9898/get-load')
    return {"worker": worker, "load": res.json()}

@app.route('/get-load', methods=['GET'])
def getLoad():
    logging.info('Getting load')
    start = time.time()
    system_load = []
    threads = []
    for worker in module_config['workers']:
        logging.info('Getting load for worker: ' + worker['name'])
        t = threading.Thread(target=lambda: system_load.append(get_load_thread(worker)))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    time_taken = time.time() - start
    logging.info('Got load in ' + str(time_taken) + ' seconds')
    return jsonify(system_load)

def start():
    app.run(port=9999, host='0.0.0.0')
