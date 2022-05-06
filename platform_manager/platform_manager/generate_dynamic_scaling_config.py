import json
from uuid import uuid4

platform_config = json.loads(open("platform_config.json").read())
subscription_id = platform_config["subscription_id"]
location = platform_config["master"]["location"]
password = platform_config["master"]["passwd"]

server = {
    "workers": [
        {
            "user": 'w'+str(uuid4())[:4],
            "name": 'w'+str(uuid4())[:4],
            "ip": "",
            "passwd": password,
            "location": location,
        }

    ],
    "subscription_id": subscription_id,
}
with(open("dynamic_servers.json", "w")) as f:
    json.dump(server, f)
