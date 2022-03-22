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
    logging.info("ModelId: {}".format(ModelId))
    with open('/tmp/model.zip', 'wb') as f:
        f.write(model['content'])
    logging.info('Got model: {}'.format(ModelId), ' from mongo')
    container_name = aiDeployer.run('/tmp/model.zip')
    res = Deploy(path='ai_deployer', container_name=container_name)
    logging.info('Deployed model: {}'.format(ModelId),
                 ' to container: {}'.format(container_name))
    os.remove('/tmp/model.zip')
    logging.info('Removed model.zip from /tmp')
    shutil.rmtree('ai_deployer/model')
    logging.info('Removed model folder from ai_deployer')
    return res


@app.route('/app', methods=['POST'])
def deploy_app():
    ApplicationID = request.json['ApplicationID']
    logging.info("ApplicationID: {}".format(ApplicationID))
    sensor_id = str(request.json['sensor_ids'][0])
    application = db.applications.find_one({"ApplicationID": ApplicationID})
    with open('/tmp/app.zip', 'wb') as f:
        f.write(application['content'])
    logging.info('Got application: {}'.format(ApplicationID), ' from mongo')
    container_name = appDeployer.run('/tmp/app.zip', sensor_id)
    res = Deploy(path='app_deployer', container_name=container_name)
    logging.info('Deployed application: {}'.format(ApplicationID),
                 ' to container: {}'.format(container_name))
    os.remove('/tmp/app.zip')
    logging.info('Removed app.zip from /tmp')
    shutil.rmtree('app_deployer/app')
    logging.info('Removed app folder from app_deployer')
    return res


def start():
    app.run(port=9999, host='0.0.0.0')
