import threading
import random
import time
from flask import Flask

app = Flask(__name__)

temp = random.randint(-10, 50)

def change_data():
	global temp
	while True:
		time.sleep(2)
		temp = random.randint(-10, 50)

heat_thread = threading.Thread(target=change_data)

@app.route('/')
def get_temperature():
	global temp
	return str(temp)

if __name__ == '__main__':
	heat_thread.start()
	app.run(port=8085, debug=True)
	heat_thread.join()

