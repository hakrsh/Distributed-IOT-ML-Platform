import threading
import random
import time
from flask import Flask
from data import get_passengers

app = Flask(__name__)

i = 0
val = random.randint(97, 99)
critical_range = list(range(94,98)) + list(range(100,106))

def change_data():
	global val
	global i
	while True:
		time.sleep(2)
		val = random.randint(97, 99)
		i += 1
		if i > 30:
			val = random.choice(critical_range)
		if i == 35:
			i = 0

thread = threading.Thread(target=change_data)

@app.route('/')
def get_spo2():
	global val
	return str(val)

if __name__ == '__main__':
	thread.start()
	app.run(port=7071, host='0.0.0.0')
	thread.join()
