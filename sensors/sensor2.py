import threading
import random
import time
from flask import Flask

app = Flask(__name__)

R = random.randint(0, 255)
G = random.randint(0, 255)
B = random.randint(0, 255)

def change_data():
	global R
	global G
	global B
	while True:
		time.sleep(3)
		R = random.randint(0, 255)
		G = random.randint(0, 255)
		B = random.randint(0, 255)

rgb_thread = threading.Thread(target=change_data)

@app.route('/')
def get_temperature():
	global R
	global G
	global B
	return str(R)+":"+str(G)+":"+str(B)

if __name__ == '__main__':
	rgb_thread.start()
	app.run(port=8083, debug=True)
	rgb_thread.join()