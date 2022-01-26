from zumi.util.camera import Camera
from zumi.util.vision import Vision
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import threading
import os
import cv2
import argparse
import subprocess

class StreamingGenerator:
    def __init__(self, camera, socket):
        self.outputFrame = None
        self.lock = threading.Lock()
        self.camera = camera
        self.camera.start_camera()
        self.mode = 'color'
        self.socket = socket


    def setup_face_detection(self):
        self.face_detector = cv2.CascadeClassifier("/usr/local/lib/python3.5/dist-packages/zumi/util/src/haarcascade_frontalface_default.xml")
        self.scale_factor = 1.2
        self.min_neighbors = 5
        self.min_size = 5
        self.max_size = 240
        self.faces = ()
        self.detecting = False


    def setup_vision(self):
        self.vision = Vision()


    def detect_faces(self):
        gray = cv2.cvtColor(self.outputFrame, cv2.COLOR_BGR2GRAY)
        self.faces = self.face_detector.detectMultiScale(gray, scaleFactor=self.scale_factor,
                                                    minNeighbors=self.min_neighbors,
                                                    minSize=(self.min_size, self.min_size),
                                                    maxSize=(self.max_size, self.max_size))
        self.detecting = False


    def capturing(self):
        while True:
            frame = self.camera.capture()

            if self.mode == 'gray':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            cv2.imwrite('/home/pi/Dashboard/DriveImg/drivescreen.jpg', frame)

            with self.lock:
                self.outputFrame = frame.copy()


    def generate(self):
        while True:
            with self.lock:
                if self.outputFrame is None:
                    continue

                if self.mode == 'face_detection' or self.mode == 'face':
                    self.detecting = True
                    threading.Thread(target=self.detect_faces).start()

                    for (x, y, w, h) in self.faces:
                        cv2.rectangle(self.outputFrame, (x, y), (x + w, y + h), (255, 255, 255), 4)
                elif self.mode == 'qr':
                    obj = self.vision.find_QR_code(self.outputFrame, draw_color=(0, 207, 187))
                    if obj is not None:
                        self.socket.emit('qr_msg', obj.data.decode("utf-8"))
                elif self.mode == 'object_stop':
                    obj = self.vision.find_stop_sign(self.outputFrame)
                    print(obj)

                (flag, encodedImage) = cv2.imencode(".jpg", self.outputFrame)

                if not flag:
                    continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')
app.camera = Camera(320, 240)
app.streamingGenerator = StreamingGenerator(app.camera, socketio)
t = threading.Thread(target=app.streamingGenerator.capturing)
t.daemon = True
t.start()


@app.route('/')
def index():
   return render_template('drivescreen.html')


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/video_feed')
def video_feed():
    return Response(app.streamingGenerator.generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('change_mode')
def change_mode(mode_name):
    if mode_name == 'face_detection' or mode_name == 'face':
        app.streamingGenerator.setup_face_detection()
    elif mode_name == 'qr' or mode_name == 'object_stop':
        app.streamingGenerator.setup_vision()
    app.streamingGenerator.mode = mode_name


@socketio.on('change_parameters')
def change_parameters(data):
    print(data)
    try:
        app.streamingGenerator.scale_factor = float(data[0])
        app.streamingGenerator.min_neighbors = int(data[1])
        app.streamingGenerator.min_size = int(data[2])
        app.streamingGenerator.max_size = int(data[3])
    except:
        print('error')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--protocol", type=str, required=True, help="https or http")
    args = vars(ap.parse_args())

    if os.path.isdir('/home/pi/Dashboard/DriveImg/') == False:
        os.mkdir('/home/pi/Dashboard/DriveImg/')

    if args["protocol"] == "https":
        app.run(host='0.0.0.0', debug=True, threaded=True, port=3456, use_reloader=False, ssl_context=(
        "/usr/local/lib/python3.5/dist-packages/zumidashboard/crt/zumidashboard_ai.crt",
        "/usr/local/lib/python3.5/dist-packages/zumidashboard/crt/private.key"))
    else:
        socketio.run(app, debug=True, host='0.0.0.0', port=3456, use_reloader=False)
        # app.run(host='0.0.0.0', debug=True, threaded=True, port=3456, use_reloader=False)
