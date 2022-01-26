from flask import current_app
import os, subprocess, time


lib_dir = os.path.dirname(os.path.abspath(__file__))


def start_streaming_server():
    current_app.config["OPENING_STREAMING_SERVER_PROC"] = subprocess.Popen(
        ['python3', os.path.dirname(os.path.abspath(__file__)) + '/webstreaming.py', '--protocol', 'http'])


def check_camera_connection():
    try:
        subprocess.Popen(['fuser', '-k', '3456/tcp'])
        time.sleep(1)
    except:
        print('The streaming server was not running')

    from zumi.util.camera import Camera

    try:
        camera = Camera(auto_start=True)
        frame = camera.capture()
        camera.close()
        return True
    except:
        return False


def check_streaming_server():
    p = subprocess.Popen(
        ['sudo', 'bash', '/usr/local/lib/python3.5/dist-packages/zumidashboard/shell_scripts/check_port.sh', '3456'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    p.wait()
    if len(stdout) > 1:
        print('The streaming server is not running')
        return False
    else:
        print('The streaming server is running')
        return True


def kill_streaming_server():
    subprocess.Popen(['fuser', '-k', '3456/tcp'])
    subprocess.Popen(['fuser', '-k', '9696/tcp'])

    try:
        current_app.config['OPENING_STREAMING_SERVER_PROC'].kill()
        print('Killed opening streaming server process')
    except:
        print('There was no opening streaming server process')

