import threading
import random
import time
import json
from flask import Flask, render_template, request

app = Flask(__name__)

state = 0

@app.route('/home')
def get_home():
	return render_template("index.html", state=state)

@app.route('/get_signal')
def get_data():
	global state
	return json.dumps(state)

@app.route('/',  methods = ['POST'])
def put_data():
	global state
	data = request.data
	state = int(json.loads(data)["signal"])
	return "Done!"

if __name__ == '__main__':
	app.run(port=7778, host='0.0.0.0')


