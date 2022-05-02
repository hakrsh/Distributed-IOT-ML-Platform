import json
import shutil
from deployer import module_config
from jinja2 import Template
import importlib.resources as pkg_resources
import logging
logging.basicConfig(level=logging.INFO)


def run(package, sensors, controllers, app_id,app_contract):
    import zipfile
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('/tmp/'+app_id)
    logging.info('Extracted package: ' + package)
    image_name = app_contract['name']
    logging.info('Generating sensor interface')
    template = Template(pkg_resources.read_text('deployer.app_deployer','sensor_template.j2'))
    with open(f'/tmp/{app_id}/{app_contract["sensor_interface"]}', 'w') as f:
        f.write(template.render(sensors=sensors,sensor_api=module_config['sensor_api']))
    logging.info('Generated ' + app_contract['sensor_interface'])

    logging.info('Generating controller interface')
    for controller in controllers:
        args = ''
        for arg in controller['args']:
            args += arg['name'] + ', '
        controller['args_list'] = args[:-2]
    template = Template(pkg_resources.read_text('deployer.app_deployer','controller_template.j2'))
    with open(f'/tmp/{app_id}/{app_contract["controller_interface"]}', 'w') as f:
        f.write(template.render(controllers=controllers,controller_api=module_config['sensor_api']))
    logging.info('Generated ' + app_contract['controller_interface'])

    with open(f'/tmp/{app_id}/{app_contract["model_interface"]}', 'w') as f:
        f.write(json.dumps(app_contract['models']))
    logging.info('Generated ' + app_contract['model_interface'])
    
    shutil.move(f'/tmp/{app_id}/{app_contract["requirements"]}', f'/tmp/{app_id}/requirements.txt')
    logging.info('Moved requirements.txt')
    template = Template(pkg_resources.read_text('deployer.app_deployer','dockerfile_template.j2'))
    with open(f'/tmp/{app_id}/Dockerfile', 'w') as f:
        f.write(template.render(contract=app_contract))
    logging.info('Generated Dockerfile')
    logging.info('Ready to build the app image')
    return image_name
