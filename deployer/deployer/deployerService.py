from flask import jsonify, request
from deployer.ai_deployer import aiDeployer
from deployer.app_deployer import appDeployer
from deployer.deploy import Deploy, stopInstance, systemStats
from deployer import app, db, module_config, fs
import logging
import threading
import uuid

logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return 'Deployer is running on ' + module_config['host_name'] + '@' + module_config['host_ip']


def deploy_model_thread(model_id, instance_id,job_id):
    model = db.models.find_one({"ModelId": model_id})
    logging.info("ModelId: " + model_id)
    with open(f'/tmp/{instance_id}.zip', 'wb') as f:
        f.write(fs.get(model['content']).read())
    logging.info('Got model: ' + model_id + ' from database')
    aiDeployer.run(f'/tmp/{instance_id}.zip', instance_id,model['contract'])
    threading.Thread(target=Deploy, kwargs={'dockerfile_path': f'/tmp/{instance_id}',
                     'image_tag': model['ModelName'].lower(), 'instance_id': instance_id, 'package': instance_id,'job_id':job_id}).start()


@app.route('/model', methods=['POST'])
def deploy_model():
    model_id = request.json['ModelId']
    logging.info('ModelID: ' + model_id)
    instance_id = request.json['InstanceId']
    logging.info("InstanceID: " + instance_id)
    logging.info("Creating deployment record")
    job_id = str(uuid.uuid4())[:8]
    db.jobs.insert_one({"type": "model","status": "pending", "instance_id": instance_id, "model_id": model_id, "job_id": job_id})
    logging.info("Job created")
    db.instances.update_one({"instance_id": instance_id}, {"$set": {"status": "pending"}})
    logging.info("Instance status updated")
    threading.Thread(target=deploy_model_thread,
                     args=(model_id, instance_id,job_id)).start()
    return {"InstanceID": instance_id, "Status": "pending"}


def deploy_app_thread(application_id, app_name, sensors, controllers, instance_id,job_id):
    application = db.applications.find_one({"ApplicationID": application_id})
    with open(f'/tmp/{instance_id}.zip', 'wb') as f:
        f.write(fs.get(application['content']).read())
    logging.info('Got application: ' + application_id + ' from database')
    appDeployer.run(
        f'/tmp/{instance_id}.zip', sensors, controllers, instance_id, application['app_contract'])
    threading.Thread(target=Deploy, kwargs={'dockerfile_path': f'/tmp/{instance_id}',
                     'image_tag': app_name, 'instance_id': instance_id, 'package': instance_id,'job_id':job_id}).start()


@app.route('/app', methods=['POST'])
def deploy_app():
    application_id = request.json['ApplicationID']
    app_name = request.json['app_name'].lower()
    sensors = request.json['sensor_ids']
    controllers = request.json['controller_ids']
    sched_id = request.json['sched_id']
    instance_id = request.json['InstanceId']
    logging.info("Creating deployment record: " + app_name)
    job_id = str(uuid.uuid4())[:8]
    db.jobs.insert_one({"type": "app","status": "pending", "instance_id": instance_id, "application_id": application_id, "app_name":app_name, "sensor_ids": sensors, "controller_ids": controllers, "sched_id": sched_id, "job_id": job_id})
    logging.info("Job created")
    db.instances.update_one({"instance_id": instance_id}, {"$set": {"status": "pending"}})
    logging.info("Instance status updated")
    threading.Thread(target=deploy_app_thread, args=(
        application_id, app_name, sensors, controllers, instance_id,job_id)).start()
    return {"InstanceID": instance_id,"sched_id":sched_id, "Status": "pending"}


@app.route('/stop-instance', methods=['POST'])
def stop_instance():
    instance_id = request.json['InstanceID']
    container_id = request.json['ContainerID']
    logging.info("InstanceID: " + instance_id)
    logging.info("ContainerID: " + container_id)
    job_id = str(uuid.uuid4())
    db.jobs.insert_one({"type": "stop_instance","status": "pending", "instance_id": instance_id, "container_id": container_id, "job_id": job_id})
    threading.Thread(target=stopInstance, kwargs={
                     'instance_id': instance_id, 'container_id': container_id,'job_id': job_id}).start()
    return {"InstanceID": instance_id, "Status": "stopping"}

def execute_job(job_id):
    job = db.jobs.find_one({"job_id": job_id})
    if job['type'] == 'model':
        deploy_model_thread(job['model_id'], job['instance_id'],job_id)
    elif job['type'] == 'app':
        deploy_app_thread(job['application_id'], job['sensor_ids'], job['controller_ids'], job['instance_id'],job_id)
    elif job['type'] == 'stop_instance':
        stopInstance(job['instance_id'], job['container_id'], job['job_id'],job_id)
    else:
        logging.info("Job type not recognized")

def pending_jobs():
    jobs = db.jobs.find({"status": "pending"})
    for job in jobs:
        execute_job(job['job_id'])

@app.route('/get-load', methods=['GET'])
def get_load():
    return jsonify(systemStats())


def start():
    app.run(port=9898, host='0.0.0.0')
