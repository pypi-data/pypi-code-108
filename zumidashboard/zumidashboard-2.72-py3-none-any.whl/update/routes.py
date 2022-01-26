from flask import Blueprint, current_app
from zumidashboard import socketio, zumi, screen
from zumidashboard.scripts import check_content_missing, check_user_content_missing
import zumidashboard.updater as updater
import re
import subprocess
import os

update = Blueprint('update', __name__, static_url_path="",
                   static_folder='../dashboard')


check_update_content = False


def __set_updateconf(_version="develop", _language="None"):
    with open("/etc/.updateconf", "w") as update_info:
        update_info.write("args1={}\n".format(_version))
        update_info.write("args2={}".format(_language))


@socketio.on('update_firmware')
def update_firmware():
    print('update firmware from dashboard')
    version = re.findall(
        '[0-9]+.[0-9]+', current_app.config['INTERNET_INFO']["latest_dashboard_version"])[0]
    __set_updateconf(_version=version)
    subprocess.Popen(['sudo', 'systemctl', 'start', 'zumi_updater.service'])


@socketio.on('update_everything')
def update_everything():
    print('update firmware & content from dashboard')
    version = re.findall(
        '[0-9]+.[0-9]+', current_app.config['INTERNET_INFO']["latest_dashboard_version"])[0]
    __set_updateconf(_version=version,
                     _language=current_app.config['LANGUAGE'])
    subprocess.Popen(['sudo', 'systemctl', 'start', 'zumi_updater.service'])


@socketio.on('update_content')
def update_content(language="en"):
    global check_update_content
    print('update content from dashboard')
    check_update_content = False
    updater.update_content(zumi, screen, language)
    check_update_content = True


@socketio.on('check_update_content')
def check_update_content():
    global check_update_content
    print(check_update_content)
    socketio.emit('check_update_content', check_update_content)


@socketio.on('check_content_missing')
def _check_content_missing():
    check_content = check_content_missing(current_app.config['LANGUAGE'])
    socketio.emit('check_content_missing', check_content)


@socketio.on('check_user_content_missing')
def _check_user_content_missing():
    print('check user content missing')
    check_user_content = check_user_content_missing(
        current_app.config['USER'], current_app.config['LANGUAGE'])
    socketio.emit('check_user_content_missing', check_user_content)
    print(check_user_content)


@socketio.on('update_true')
def update_true():
    screen.draw_text_center("I can update")


@socketio.on('update_false')
def update_false():
    screen.hello()


@socketio.on('check_just_updated')
def check_just_updated():
    print('app.py: check_just_updated')
    try:
        if os.path.exists('/home/pi/Dashboard/update/justUpdated'):
            socketio.emit('check_just_updated', True)
            os.remove('/home/pi/Dashboard/update/justUpdated')
    except:
        print('error: check_just_updated()')


# confirm content updating is finished
@socketio.on('open_eyes')
def open_eyes():
    screen.hello()


@update.route('/develop')
def develop():
    print('update develop firmware from dashboard')
    __set_updateconf()
    subprocess.Popen(['sudo', 'systemctl', 'start', 'zumi_updater.service'])
    return update.send_static_file('index.html')
