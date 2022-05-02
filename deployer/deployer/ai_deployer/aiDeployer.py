import logging
from jinja2 import Template
import zipfile
import shutil
import importlib.resources as pkg_resources
logging.basicConfig(level=logging.INFO)


def run(package, model_id,model_contract):
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('/tmp/'+model_id)
    logging.info('Extracted package: ' + package)
    template = Template(pkg_resources.read_text('deployer.ai_deployer','server.j2'))
    with open(f'/tmp/{model_id}/server.py', 'w') as f:
        f.write(template.render(contract=model_contract))
    logging.info('Generated server.py')
    shutil.move(f'/tmp/{model_id}/{model_contract["requirements"]}', f'/tmp/{model_id}/requirements.txt')
    logging.info('Moved requirements.txt')
    template = Template(pkg_resources.read_text('deployer.ai_deployer','dockerfile_template.j2'))
    with open(f'/tmp/{model_id}/Dockerfile', 'w') as f:
        f.write(template.render(contract=model_contract))
    logging.info('Generated Dockerfile')
    logging.info('Ready to build the model image')
