import random
import time
from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

cap = cv2.VideoCapture('./test.mp4') 

# def gen_frames():
#     while(cap.isOpened()): 
#         ret, frame = cap.read()    
#         if ret:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#         else:
#            print('no video')
#            cap.set(cv2.CAP_PROP_POS_FRAMES, 2)
#            continue
#         if cv2.waitKey(2) & 0xFF == ord('q'):
#             break

def gen_frame():
    global cap
    ret, frame = cap.read()
    if ret:
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return frame
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
        ret, frame = cap.read()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return frame
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_frame')
def video_frame():
    return Response(gen_frame(), mimetype='image/gif')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	app.run(port=8085, host='0.0.0.0')