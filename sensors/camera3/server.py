import random
import time
from flask import Flask, render_template, Response
import cv2
import os 

app = Flask(__name__)

images = os.listdir('images')

def gen_frame():
    index = random.randint(0, len(images)-1)
    file = images[index]
    frame = cv2.imread("images/{}".format(file))
    ret, buffer = cv2.imencode('.jpg', frame)
    data = buffer.tobytes()
    return data

@app.route('/')
def video_frame():
    return gen_frame()

if __name__ == '__main__':
	app.run(port=8085, host='0.0.0.0')
