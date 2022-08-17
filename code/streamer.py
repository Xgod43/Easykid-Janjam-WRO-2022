#!/usr/bin/env python
from flask import Flask, render_template, Response
from camera import camera
import threading
import cv2

cam = camera()
vs = threading.Thread(target=cam.update, daemon=True)
vs.start()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    global vs
    while True:
        _, frame = cam.get()
        if not _:
            print('No frame')
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    vs.release()