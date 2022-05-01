import random
import time
from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def gen_frames():  
    while True:
        success, frame = camera.read() # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_frame():  
    success, frame = camera.read() 
    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_frame')
def video_frame():
    return Response(gen_frame(), mimetype='image/gif')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	app.run(port=8085, host='0.0.0.0')
