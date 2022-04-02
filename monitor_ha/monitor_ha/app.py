from flask import Flask, render_template, request

logging.basicConfig(level=logging.INFO)

monitor_interval = 1

mongo_server = module_config["mongo_server"]

client = pymongo.MongoClient(mongo_server)
logging.info('Connected to database')

db = client[ "repo" ]
instances = db["instances"]
logging.info('instance database created')

@app.route('/start')
def start():
    return "started monitoring", 200


@app.route('/stop')
def start():
    return "stop monitoring", 200