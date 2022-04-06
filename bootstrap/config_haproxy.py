import logging
import json
from jinja2 import Template

logging.basicConfig(level=logging.INFO)

logging.info('Reading config servers.json')
servers = json.loads(open('servers.json').read())

def render_template(template_file, output_file, workers):
    with open(template_file) as f:
        template = Template(f.read())
    with open(output_file, 'w') as f:
        f.write(template.render(servers=workers))

def generate_config():
    workers = []
    for worker in servers['workers']:
        temp = {}
        temp['name'] = worker['user']
        temp['ip'] = worker['ip']
        workers.append(temp)
    render_template('haproxy.j2', 'haproxy.cfg', workers=workers)

generate_config()