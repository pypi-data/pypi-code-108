from flask import current_app
from zumidashboard import zumi, screen
from gpiozero import CPUTemperature
import zumidashboard.sounds as sound
import psutil, uuid, re, time


def hardware_info():
    cpu_info = str(int(psutil.cpu_percent()))
    ram_info = str(int(psutil.virtual_memory().percent))
    mac_address = str(':'.join(re.findall('..', '%012x' % uuid.getnode())))
    cpu_temp = CPUTemperature(min_temp=50, max_temp=90)
    cpu_temp_info = str(int(cpu_temp.temperature))
    try:
        with open('/home/pi/Dashboard/Zumi_Content_{}/README.md'.format(current_app.config['LANGUAGE']), 'r') as zumiContentVersionFile:
            content_version = zumiContentVersionFile.readline().replace("\n", "")
    except:
        content_version = ''
    board_version = str(zumi.get_board_firmware_version())

    hardware_info = {"cpu_info": cpu_info, "ram_info": ram_info, "mac_address": mac_address,
                     "cpu_temp": cpu_temp_info, "content_version": content_version, "board_version": board_version}

    return hardware_info


def recalibrate():
    screen.draw_text_center("Place me on\na flat surface.", font_size=18)
    sound.happy_sound(zumi)
    time.sleep(5)
    screen.calibrating()
    sound.try_calibrate_sound(zumi)
    zumi.calibrate_gyro()
    time.sleep(3)
    screen.draw_image_by_name("calibrated")
    sound.calibrated_sound(zumi)


def screen_hello():
    screen.hello()


def awake():
    screen.hello()
    sound.wake_up_sound(zumi)

