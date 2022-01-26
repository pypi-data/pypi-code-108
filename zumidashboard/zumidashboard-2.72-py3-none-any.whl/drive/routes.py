from flask import Blueprint
from threading import Thread
from zumi.zumi import Zumi
from zumidashboard import socketio, zumi, screen, personality
from zumidashboard.drive.utils import drive_open_eyes
from zumidashboard.drive_mode import DriveMode
import time
import subprocess
import zumidashboard.sounds as sounds


drive = Blueprint('drive', __name__, static_url_path="",
                  static_folder='../dashboard')

drive_mode = DriveMode(zumi)


@drive.route('/drive-mode')
def drive_mode_page():
    return drive.send_static_file('index.html')


@socketio.on('stop_motors')
def stop_motors():
    zumi = Zumi()


@socketio.on('zumi_direction')
def zumi_direction(input_key):
    drive_mode.zumi_direction(input_key)


@socketio.on('zumi_celebrate')
def zumi_celebrate():
    screen.clear()
    personality.celebrate()
    Thread(target=drive_open_eyes, args=(5,)).start()


@socketio.on('zumi_happy')
def zumi_happy():
    screen.clear()
    personality.happy()
    Thread(target=drive_open_eyes, args=(5,)).start()


@socketio.on('zumi_awake')
def zumi_awake():
    screen.clear()
    personality.awake()
    Thread(target=drive_open_eyes, args=(5,)).start()


@socketio.on('zumi_angry')
def zumi_angry():
    screen.clear()
    personality.angry()
    Thread(target=drive_open_eyes, args=(5,)).start()


@socketio.on('zumi_stop')
def zumi_stop():
    drive_mode.zumi_stop()


@socketio.on('display_text')
def display_text(txt):
    screen.clear()
    sounds.calibrated_sound(zumi)
    if txt == '':
        screen.hello()
        return
    screen.draw_text_center(txt)
    Thread(target=drive_open_eyes, args=(15,)).start()


@socketio.on('recalibrate')
def recalibrate():
    screen.draw_text_center("Place me on\na flat surface.", font_size=18)
    sounds.happy_sound(zumi)
    time.sleep(5)
    screen.calibrating()
    sounds.try_calibrate_sound(zumi)
    zumi.calibrate_gyro()
    time.sleep(3)
    socketio.emit("calibrated")
    screen.draw_image_by_name("calibrated")
    sounds.calibrated_sound(zumi)
    time.sleep(5)
    screen.hello()
