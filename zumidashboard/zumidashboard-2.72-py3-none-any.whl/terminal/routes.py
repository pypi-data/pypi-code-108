from flask import Blueprint, send_from_directory
from zumidashboard import socketio
import zumidashboard.terminal.utils as utils


terminal = Blueprint('terminal', __name__, static_url_path="",
                    static_folder='../dashboard')

lib_dir = '/usr/local/lib/python3.5/dist-packages/zumidashboard'


@terminal.route('/code-editor-image/<path:filename>')
def send_image_file(filename):
    return send_from_directory('/usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard', filename)


@socketio.on('run_console_server')
def run_console_server(mode):
    is_server_running = utils.run_terminal_server(mode)
    socketio.emit('run_console_server', is_server_running)


@socketio.on('check_console_server')
def check_console_server():
    running = utils.check_terminal_server_is_running()
    socketio.emit('check_console_server', running)

