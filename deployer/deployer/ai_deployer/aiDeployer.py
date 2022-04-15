import logging
from jinja2 import Template
import zipfile

logging.basicConfig(level=logging.INFO)


def run(package, model_id,model_contract):
    with zipfile.ZipFile(package, 'r') as zip_ref:
        zip_ref.extractall('/tmp/'+model_id)
    logging.info('Extracted package: ' + package)
    with open('server.h2') as f:
        template = Template(f.read())
    with open(f'/tmp/{model_id}/server.py', 'w') as f:
        f.write(template.render(contract=model_contract))
    logging.info('Generated server.py')
    
    with open('dockerfile_template.j2') as f:
        template = Template(f.read())
    with open(f'/tmp/{model_id}/Dockerfile', 'w') as f:
        f.write(template.render(dir=model_contract['root_dir']))
    logging.info('Generated Dockerfile')
    logging.info('Ready to build the model image')
