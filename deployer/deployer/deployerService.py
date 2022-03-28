import os
import shutil
from flask import request
from deployer.ai_deployer import aiDeployer
from deployer.app_deployer import appDeployer
from deployer.deploy import Deploy
from . import app, db
import logging

logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return 'Deployer is running!'


@app.route('/model', methods=['POST'])
def deploy_model():
    model_id = request.json['ModelId']
    model = db.models.find_one({"ModelId": model_id})
    logging.info("ModelId: " + model_id)
    with open(f'/tmp/{model_id}.zip', 'wb') as f:
        f.write(model['content'])
    logging.info('Got model: ' + model_id + ' from database')
    image_name = aiDeployer.run(f'/tmp/{model_id}.zip', model_id)
    res = Deploy(dockerfile_path=f'/tmp/{model_id}', image_tag=image_name)
    logging.info('Deployed model: ' + model_id +
                 ' to container: ' + res['container_id'])
    os.remove(f'/tmp/{model_id}.zip')
    logging.info('Removed temporary file: /tmp/'+model_id+'.zip')
    shutil.rmtree(f'/tmp/{model_id}/')
    logging.info('Removed temporary directory /tmp/'+model_id+'/')
    return res


@app.route('/app', methods=['POST'])
def deploy_app():
    application_id = request.json['ApplicationID']
    logging.info("ApplicationID: " + application_id)
    sensor_id = str(request.json['sensor_ids'][0])
    application = db.applications.find_one({"ApplicationID": application_id})
    with open(f'/tmp/{application_id}.zip', 'wb') as f:
        f.write(application['content'])
    logging.info('Got application: ' + application_id + ' from database')
    image_name = appDeployer.run(
        f'/tmp/{application_id}.zip', sensor_id, application_id)
    res = Deploy(
        dockerfile_path=f'/tmp/{application_id}', image_tag=image_name)
    logging.info('Deployed application: ' + application_id +
                 ' to container: ' + res['container_id'])
    os.remove(f'/tmp/{application_id}.zip')
    logging.info('Removed temporary file /tmp/'+application_id+'.zip')
    shutil.rmtree(f'/tmp/{application_id}')
    logging.info('Removed temporary directory /tmp/'+application_id+'/')
    return res


def start():
    app.run(port=9999, host='0.0.0.0')
