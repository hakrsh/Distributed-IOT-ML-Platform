import json
import threading
from flask import request, render_template
import uuid
from scheduler import app, db, client, kafka_server
import logging
from bson.json_util import dumps
import time
import schedule as sched
from datetime import datetime
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)
producer = KafkaProducer(bootstrap_servers=kafka_server, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
logging.info('Connecting to kafka')

def send(topic, message):
    producer.send(topic, message)
    sched.CancelJob

@app.route('/get-app-contract/<app_id>', methods=['GET'])
def get_app_contract(app_id):
    sensors = json.loads(dumps(client.sensors.sensordetails.find()))
    contract = db.applications.find_one({'ApplicationID': app_id})['app_contract']
    for c_sensor in contract['sensors']:
        sensor_ids = []
        for sensor_ in sensors:
            if c_sensor['sensor_type'] == sensor_['Type']:
                sensor_ids.append(sensor_['topic_id']+","+sensor_['Type']+","+sensor_['Location']+","+sensor_['Name'])
        c_sensor['sensor_ids'] = sensor_ids
    
    controllers = json.loads(dumps(client.sensors.controllerdetails.find()))
    for c_controller in contract['controllers']:
        controller_ids = []
        for controller_ in controllers:
            if c_controller['controller_type'] == controller_['Type']:
                controller_ids.append(controller_['controller_id']+","+controller_['Type']+","+controller_['Location']+","+controller_['Name'])
        c_controller['controller_ids'] = controller_ids

    return json.dumps(contract)


def format_time(time):
    time = time.replace('T', ' ')
    time = time+":00"
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return time

def schedule_app_instance(query):
    logging.info("Scheduling instance")
    time = datetime.strptime(query["start_time"], '%Y-%m-%d %H:%M:%S')
    time_to_execute = "{:02d}:{:02d}".format(time.hour,time.minute)
    sched.every().day.at(time_to_execute).do(send, topic='to_deployer_master', message=query)
    logging.info("App will be deployed at {}".format(time_to_execute))

def stop_app_instance(query):
    logging.info("Stopping instance")
    time = datetime.strptime(query["end_time"], '%Y-%m-%d %H:%M:%S')
    time_to_execute = "{:02d}:{:02d}".format(time.hour,time.minute)
    sched.every().day.at(time_to_execute).do(send, topic='to_deployer_master', message=query)
    logging.info("App will be stopped at {}".format(time_to_execute))

def get_running_apps():
    logging.info('Starting db watcher')
    logging.info('Waiting for apps to be deployed')
    while len(list(db.instances.find({'type': 'app'}))) == 0:
        continue
    instances = db.instances
    # if there any changes in instances collections update models hashmap
    for change in instances.watch():
        if change["operationType"] == "update":
            logging.info('update detected')
            document_id = change['documentKey']
            document = instances.find_one(document_id)
            if document['type'] == 'app' and document['status'] == 'running':
                logging.info('App Name: {}'.format(document['app_name']))
                url = f'http://{document["ip"]}:{document["port"]}'
                logging.info(f'url: {url}')
                db.scheduerinfo.update_one({'app_name': document['app_name']}, {'$set': {'instance_id': document['instance_id']}})

def run_schedule():
    while True:
        sched.run_pending()
        time.sleep(1)

@app.route('/', methods=['POST', 'GET'])
def schedule():
    if request.method == 'GET':
        applications = json.loads(dumps(db.applications.find()))
        controllers = json.loads(
            dumps(client.sensors.controllerdetails.find()))
        sensors = json.loads(dumps(client.sensors.sensordetails.find()))
        return render_template('index.html', app_list=applications, controller_ids=controllers, sensor_ids=sensors)
    if request.method == 'POST':
        app_id = request.form['app_id']
        app_name = request.form['instance_name']
        if db.instances.find_one({'app_name': app_name}) is not None:
            return 'App name already exists'
        app_contract = json.loads(get_app_contract(app_id))
        controllers = app_contract['controllers']
        start_time = format_time(request.form['starttime'])
        end_time = format_time(request.form['endtime'])
        cur_time = datetime.now()
        if start_time < cur_time:
            return 'Start time cannot be in the past'
        logging.info('Binding sensor to application...')
        sensor_bindings = []
        i = 1
        while True:
            if request.form.get('sensor' + str(i) + '_name') is None:
                break
            sensor_bindings.append({
                'sensor_id': request.form.get('sensor' + str(i) + '_id'),
                'sensor_name': request.form.get('sensor' + str(i) + '_name')
            })
            i += 1

        logging.info('Binding controller to application...')
        controller_bindings = {}
        i = 1
        while True:
            if request.form.get('controller' + str(i) + '_name') is None:
                break
            controller_name = request.form.get('controller' + str(i) + '_name')
            controller_bindings[controller_name] = request.form.get(
                'controller' + str(i) + '_id')
            i += 1
        for controller in controllers:
            controller['controller_id'] = controller_bindings[controller["function"]]

        logging.info('Application is ready to schedule...')
        sched_id = str(uuid.uuid4())[:8]
        query = {
            "type": "app",
            "ApplicationID": app_id,
            "app_name": app_name,
            "sensor_ids": sensor_bindings,
            "controller_ids": controllers,
            "sched_id": sched_id,
            "start_time": str(start_time),
            "end_time": str(end_time),
            "instance_id": "blank",
            "stopped_flag": False
        }
        logging.info('Creating db entry...')
        db.scheduleinfo.insert_one(query)
        logging.info('Creating scheduler entry...')
        schedule_app_instance(json.loads(dumps(query)))

        return 'Application will be scheduled on ' + str(start_time)

def schedule_pending_tasks():
    for task in db.scheduleinfo.find({"instance_id":"blank"}):
        start_time = datetime.strptime(task["start_time"], '%Y-%m-%d %H:%M:%S')
        print(start_time)
        print(datetime.now())
        if datetime.now() <= start_time:
            stop_app_instance(json.loads(dumps(task)))
    for task in db.scheduleinfo.find({"stopped_flag":False}):
        if task["instance_id"] != "blank":
            query = {
                "type": "stop",
                "instance_id":task["instance_id"]
            }
            end_time = datetime.strptime(task["end_time"], '%Y-%m-%d %H:%M:%S')
            if datetime.now() <= end_time:
                stop_app_instance(json.loads(dumps(query)))

def start():
    threading.Thread(target=run_schedule).start()
    threading.Thread(target = schedule_pending_tasks).start()
    app.run(port = 8210, host='0.0.0.0')
