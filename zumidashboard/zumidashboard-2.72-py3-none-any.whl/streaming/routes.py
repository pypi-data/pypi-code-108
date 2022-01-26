from flask import Blueprint
from zumidashboard import socketio
import zumidashboard.streaming.utils as utils


streaming = Blueprint('streaming', __name__, static_url_path="", static_folder='../dashboard')


@socketio.on('open_pi_streaming')
def _open_pi_streaming():
    utils.start_streaming_server()


@socketio.on('check_camera_connection')
def _check_camera_connection():
    connected = utils.check_camera_connection()
    socketio.emit('check_camera_connection', connected)


@socketio.on('check_streaming_server')
def _check_streaming_server():
    running = utils.check_streaming_server()
    socketio.emit('check_streaming_server', running)


@socketio.on('camera_stop')
def camera_stop():
    utils.kill_streaming_server()
