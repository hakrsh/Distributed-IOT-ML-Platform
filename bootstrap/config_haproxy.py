import json
from jinja2 import Template

workers = json.loads(open('platform_config.json').read())['workers']

def render_template(template_file, output_file, workers):
    with open(template_file) as f:
        template = Template(f.read())
    with open(output_file, 'w') as f:
        f.write(template.render(servers=workers))

render_template('haproxy.j2', 'haproxy.cfg', workers=workers)
