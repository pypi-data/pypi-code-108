from flask import Flask
from flask_socketio import SocketIO
from zumi.zumi import Zumi
from zumi.util.screen import Screen
from zumi.personality import Personality
from zumidashboard.config import CustomConfig
from threading import Thread, Event
import os
import subprocess
import threading


socketio = SocketIO()

zumi = Zumi()
screen = Screen(clear=False)
personality = Personality(zumi, screen)


class StoppableThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Failed exception raise')


def create_app(config_class=CustomConfig):
    import logging
    app = Flask(__name__, static_url_path="", static_folder='dashboard')
    app.config.from_object(config_class)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logging.handlers.RotatingFileHandler(
        '/home/pi/Dashboard/debug/dashboard.log', maxBytes=10000, backupCount=1))
    socketio.init_app(app)
    app.socketXterm = ''

    from zumidashboard.main.routes import main
    from zumidashboard.network.routes import network
    from zumidashboard.update.routes import update
    from zumidashboard.login.routes import login
    from zumidashboard.drive.routes import drive
    from zumidashboard.code_mode.routes import code_mode
    from zumidashboard.streaming.routes import streaming
    from zumidashboard.wizards.routes import wizards
    from zumidashboard.terminal.routes import terminal
    app.register_blueprint(main)
    app.register_blueprint(network)
    app.register_blueprint(update)
    app.register_blueprint(login)
    app.register_blueprint(drive)
    app.register_blueprint(code_mode)
    app.register_blueprint(streaming)
    app.register_blueprint(wizards)
    app.register_blueprint(terminal)

    return app


def firmware_updater_check():
    base = '/home/pi/Dashboard/'
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(base+'update'):
        os.mkdir(base+'update')
    if not os.path.isfile(base+'update/update_log.txt'):
        f = open(base+'update/update_log.txt', 'w')
        f.close()

    try:
        update_list = os.listdir(lib_dir + '/update_scripts/')
        for line in open(base + 'update/update_log.txt'):
            try:
                update_list.remove(line.rstrip('\n'))
            except:
                pass

    except FileNotFoundError:
        update_list = []

    if len(update_list):
        firmware_updater(update_list)
        return "updated"
    else:
        return "no update"


def firmware_updater(update_list):
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    print(update_list)
    update_list.sort()
    print(update_list)
    f = open('/home/pi/Dashboard/update/update_log.txt', 'a')
    for version in update_list:
        print("update {}".format(version))
        p = subprocess.Popen(
            ['sudo', 'sh', lib_dir + '/update_scripts/'+version, '.'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        p.wait()
        f.write(version+"\n")


def start_app(app, _debug=False):
    if not os.path.isfile('/usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/hostname.json'):
        subprocess.run(
            ["sudo ln -s /etc/hostname /usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/hostname.json"], shell=True)
    firmware_updater_check()

    p = subprocess.Popen(
        ['sudo', 'bash', '/usr/local/lib/python3.5/dist-packages/zumidashboard/shell_scripts/check_port.sh', '8443'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    p.wait()
    if len(stdout) > 1:
        p = subprocess.run(
            'sudo python3 /usr/local/lib/python3.5/dist-packages/zumidashboard/gesture.py & 2>&1', shell=True)

    socketio.run(app, debug=_debug, host='0.0.0.0', port=80)
