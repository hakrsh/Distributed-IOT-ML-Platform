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
    ModelId = request.json['ModelId']
    model = db.models.find_one({"ModelId": ModelId})
    logging.info("ModelId: " + ModelId)
    with open('/tmp/model.zip', 'wb') as f:
        f.write(model['content'])
    logging.info('Got model: ' + ModelId + ' from database')
    container_name = aiDeployer.run('/tmp/model.zip')
    res = Deploy(path='/tmp/ai_deployer', container_name=container_name)
    logging.info('Deployed model: ' + ModelId +
                 ' to container: ' + container_name)
    os.remove('/tmp/model.zip')
    logging.info('Removed temporary file: /tmp/model.zip')
    shutil.rmtree('/tmp/ai_deployer/')
    logging.info('Removed temporary directory /tmp/ai_deployer/')
    return res


@app.route('/app', methods=['POST'])
def deploy_app():
    ApplicationID = request.json['ApplicationID']
    logging.info("ApplicationID: " + ApplicationID)
    sensor_id = str(request.json['sensor_ids'][0])
    application = db.applications.find_one({"ApplicationID": ApplicationID})
    with open('/tmp/app.zip', 'wb') as f:
        f.write(application['content'])
    logging.info('Got application: ' + ApplicationID + ' from database')
    container_name = appDeployer.run('/tmp/app.zip', sensor_id)
    res = Deploy(path='/tmp/app_deployer', container_name=container_name)
    logging.info('Deployed application: ' + ApplicationID +
                 ' to container: ' + container_name)
    os.remove('/tmp/app.zip')
    logging.info('Removed temporary file /tmp/app.zip')
    shutil.rmtree('/tmp/app_deployer')
    logging.info('Removed temporary directory /tmp/app_deployer')
    return res


def start():
    app.run(port=9999, host='0.0.0.0')
