import json
import importlib.resources as pkg_resources

module_config = json.loads(pkg_resources.read_binary('monitor_ha', 'config.json'))