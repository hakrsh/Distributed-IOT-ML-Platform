import json
from jinja2 import Template

model_contract = json.loads(open('model_contract.json').read())

def render_template(template_file, output_file, model_contract):
    with open(template_file) as f:
        template = Template(f.read())
    with open(output_file, 'w') as f:
        f.write(template.render(contract=model_contract))

render_template('server.j2', 'server.py', model_contract)
