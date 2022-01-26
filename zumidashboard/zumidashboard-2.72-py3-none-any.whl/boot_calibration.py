import time
from zumi.zumi import Zumi
from zumi.util.screen import Screen
import zumidashboard.scripts as scripts
import os
import subprocess
from socket import gethostname
import zumidashboard.sounds as sound


def run():
    zumi = Zumi()
    screen = Screen()
    lib_dir = os.path.dirname(os.path.abspath(__file__))

    if os.path.isfile('/home/pi/recalibrate'):
        subprocess.Popen(['sudo', 'rm', '-rf', '/home/pi/recalibrate'])

        screen.draw_text_center("Place me on\na flat surface.",font_size=18)
        sound.happy_sound(zumi)
        time.sleep(5)

        screen.calibrating()
        sound.try_calibrate_sound(zumi)
        zumi.mpu.calibrate_MPU()

        screen.draw_image_by_name("calibrated")
        sound.calibrated_sound(zumi)

        p = subprocess.Popen(['sudo', 'chown', 'pi:pi', '/home/pi/offsets.txt'])
        p.communicate()

    time.sleep(1)
    ap = False
    for x in range(3):
        p = subprocess.Popen(['sudo', 'ifconfig'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        p.wait()
        if "ap0:" in str(stdout):
            ap = True
            break
        time.sleep(1)

    if ap:
        screen.draw_text_center("Find \"" + gethostname() + "\" in your WiFi list")
        sound.happy_sound(zumi)
    else:
        screen.draw_text_center("Uh oh, my WiFi is broken, might need replacement", font_size=14)

    while not scripts.is_device_connected():
        time.sleep(.2)
    screen.draw_image_by_name("foundme")
    sound.celebrate_sound(zumi)
    time.sleep(2)
    screen.draw_text_center("Loading dashboard...")
    while True:
        p = subprocess.Popen(
            ['sudo', 'bash', lib_dir+'/shell_scripts/check_port.sh', '80'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        p.wait()
        if len(stdout) > 1:
            print("server(port 80) is not ready")
        else:
            print("server(port 80) is ready")
            break
        time.sleep(5)
    time.sleep(1)
    screen.draw_text_center("Go to \"zumidashboard.ai\" in your browser")
    sound.happy_sound(zumi)
    time.sleep(1)



if __name__ == '__main__':
    run()
