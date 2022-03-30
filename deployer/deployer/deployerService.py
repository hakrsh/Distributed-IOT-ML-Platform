from flask import request
from deployer.ai_deployer import aiDeployer
from deployer.app_deployer import appDeployer
from deployer.deploy import Deploy, stopInstance,systemStats
from deployer import app, db, module_config
import logging
import threading

logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return 'Deployer is running on ' + module_config['host_name'] + '@' + module_config['host_ip']


def deploy_model_thread(model_id, instance_id):
    model = db.models.find_one({"ModelId": model_id})
    logging.info("ModelId: " + model_id)
    with open(f'/tmp/{instance_id}.zip', 'wb') as f:
        f.write(model['content'])
    logging.info('Got model: ' + model_id + ' from database')
    image_name = aiDeployer.run(f'/tmp/{instance_id}.zip', instance_id)
    threading.Thread(target=Deploy, kwargs={'dockerfile_path': f'/tmp/{instance_id}',
                     'image_tag': image_name, 'instance_id': instance_id, 'package': instance_id}).start()


@app.route('/model', methods=['POST'])
def deploy_model():
    model_id = request.json['ModelId']
    logging.info('ModelID: ' + model_id)
    instance_id = request.json['InstanceId']
    logging.info("InstanceID: " + instance_id)
    threading.Thread(target=deploy_model_thread,
                     args=(model_id, instance_id)).start()
    return {"InstanceID": instance_id, "Status": "pending"}


def deploy_app_thread(application_id, sensor_id, instance_id):
    application = db.applications.find_one({"ApplicationID": application_id})
    with open(f'/tmp/{instance_id}.zip', 'wb') as f:
        f.write(application['content'])
    logging.info('Got application: ' + application_id + ' from database')
    image_name = appDeployer.run(
        f'/tmp/{instance_id}.zip', sensor_id, instance_id)
    threading.Thread(target=Deploy, kwargs={'dockerfile_path': f'/tmp/{instance_id}',
                     'image_tag': image_name, 'instance_id': instance_id, 'package': instance_id}).start()


@app.route('/app', methods=['POST'])
def deploy_app():
    application_id = request.json['ApplicationID']
    sensor_id = str(request.json['sensor_ids'][0])

    logging.info("ApplicationID: " + application_id)
    instance_id = request.json['InstanceId']
    threading.Thread(target=deploy_app_thread, args=(
        application_id, sensor_id, instance_id)).start()
    return {"InstanceID": instance_id, "Status": "pending"}


@app.route('/stop-instance', methods=['POST'])
def stop_instance():
    instance_id = request.json['InstanceID']
    container_id = request.json['ContainerID']
    logging.info("InstanceID: " + instance_id)
    logging.info("ContainerID: " + container_id)
    threading.Thread(target=stopInstance, kwargs={'instance_id': instance_id, 'container_id': container_id}).start()
    return {"InstanceID": instance_id, "Status": "stopping"}

@app.route('/get-load', methods=['GET'])
def get_load():
    return systemStats()

def start():
    app.run(port=9898, host='0.0.0.0')
