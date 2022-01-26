from flask import Flask
from flask_socketio import SocketIO
from zumi.zumi import Zumi
from zumidashboard.drive_mode import DriveMode
import time, subprocess, os
import logging
from logging.handlers import RotatingFileHandler

if not os.path.isdir('/home/pi/Dashboard/debug'):
    os.mkdir('/home/pi/Dashboard/debug')

app = Flask(__name__, static_url_path="", static_folder='dashboard')
app.zumi = Zumi()
app.action = ''
app.action_payload = ''
socketio = SocketIO(app)
handler = RotatingFileHandler('/home/pi/Dashboard/debug/dashboard.log', maxBytes=10000, backupCount=1)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
lib_dir = os.path.dirname(os.path.abspath(__file__))
app.drive_mode = DriveMode(app.zumi)
app.drive_thread = ''
app.opening_streaming_server_proc = ''


def log(msge):
    app.logger.info(time.strftime('{%Y-%m-%d %H:%M:%S} ') + msge)


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# network connect -------------------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():
    return app.send_static_file('index.html')


@socketio.on('disconnect')
def test_disconnect():
    print('Socket disconnected')
    log('client disconnected')

    try:
        app.opening_streaming_server_proc.kill()
        print('Kill opening streaming server')
    except:
        print('There was no opening streaming server')


@socketio.on('connect')
def test_connect():
    print('a client is connected')
    log('a client is connected')
    log(app.action)
    if app.action == 'check_internet' or app.action == 'check_last_network':
        time.sleep(1)
        socketio.emit(app.action, app.action_payload)
        app.action = ''
        app.action_payload = ''


@socketio.on('check_camera_connection')
def check_camera_connection():
    try:
        subprocess.Popen(['fuser', '-k', '3456/tcp'])
        time.sleep(1)
    except:
        print('streaming server was not opened')

    from zumi.util.camera import Camera
    try:
        camera = Camera(auto_start=True)
        frame = camera.capture()
        camera.close()
        socketio.emit('check_camera_connection', True)
    except:
        socketio.emit('check_camera_connection', False)


@socketio.on('check_streaming_server')
def check_streaming_server():
    p = subprocess.Popen(
        ['sudo', 'bash', lib_dir + '/shell_scripts/check_port.sh', '3456'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    p.wait()
    if len(stdout) > 1:
        print('streaming server is not ready')
        socketio.emit('check_streaming_server', False)
    else:
        print('streaming server is ready')
        socketio.emit('check_streaming_server', True)


@socketio.on('camera_stop')
def camera_stop():
    print('Shut down streaming server')
    subprocess.Popen(['fuser', '-k', '3456/tcp'])

    try:
        app.opening_streaming_server_proc.kill()
        print('Kill opening streaming server')
    except:
        print('There was no opening streaming server')


@app.route('/gesture')
def gesture():
    return app.send_static_file('index.html')


@socketio.on('open_pi_streaming')
def open_pi_streaming():
    app.opening_streaming_server_proc = subprocess.Popen(
        ['python3', os.path.dirname(os.path.abspath(__file__)) + '/streaming/webstreaming.py', '--protocol', 'https'])


@socketio.on('gesture_move')
def gesture_move(id):
    if id == 0:
        input_key = "ArrowUp"
    elif id == 1:
        app.drive_mode.zumi_stop()
        return
    elif id == 2:
        input_key = "ArrowLeft"
    elif id == 3:
        input_key = "ArrowRight"
    app.drive_mode.zumi_direction(input_key)


@socketio.on('zumi_stop')
def zumi_stop():
    app.drive_mode.zumi_stop()


# main ----------------------------------------------------------------------------------------------------
def run(_debug=False):
    socketio.run(app, debug=_debug, host='0.0.0.0',
                 certfile="/usr/local/lib/python3.5/dist-packages/zumidashboard/crt/zumidashboard_ai.crt",
                 keyfile="/usr/local/lib/python3.5/dist-packages/zumidashboard/crt/private.key", port=8443)


if __name__ == '__main__':
    run()
