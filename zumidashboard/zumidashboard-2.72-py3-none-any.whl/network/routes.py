from flask import Blueprint, current_app
from zumi.protocol import Note
from zumidashboard import socketio, zumi, screen
from zumidashboard.utils import set_backend_language
from zumidashboard.network.utils import CheckInternetThread, ConnectWifiThread
import zumidashboard.sounds as sounds
import zumidashboard.scripts as scripts
import time


network = Blueprint('network', __name__, static_url_path="",
                    static_folder='../dashboard')


check_internet_thread = ''
connect_wifi_thread = ''
internet_object = {}


@socketio.on('ssid_list')
def ssid_list(sid):
    print('getting ssid list')
    current_app.config["ACTION"] = 'ssid_list'
    # log_info('getting ssid list')
    if current_app.config["WIFI_MSG"]:
        current_app.config["WIFI_MSG"] = False
    wifi_dict = scripts.get_ssid_list()
    print(wifi_dict)
    socketio.emit('ssid_list', wifi_dict)


@socketio.on('connect_wifi')
# def connect_wifi(ssid, passwd, isHiddenNetwork, isEnterprise):
def connect_wifi(ssid, username, passwd, isHiddenNetwork):
    global connect_wifi_thread

    print('connect wifi')
    current_app.config["INTERNET_INFO"] = ''
    current_app.config["CHECKED_INTERNET"] = False
    # connect_wifi_thread = ConnectWifiThread(
    #     ssid, passwd, isHiddenNetwork, isEnterprise)
    connect_wifi_thread = ConnectWifiThread(
        ssid, username, passwd, isHiddenNetwork)
    connect_wifi_thread.start()
    current_app.config["WIFI_MSG"] = True
    current_app.config["CONNECTED_WIFI"] = True


@socketio.on('connect_wifi_result')
def connect_wifi_result():
    global connect_wifi_thread

    try:
        if connect_wifi_thread.is_alive():
            socketio.emit('connect_wifi_result', 'in_progress')
        else:
            socketio.emit('connect_wifi_result',
                          current_app.config["CONNECTED_WIFI"])
    except Exception as e:
        print(e)


@socketio.on('zumi_success')
def zumi_success():
    global internet_object

    screen.draw_text_center(
        "I'm connected to \"" + internet_object["internet_info"]["network_name"] + "\"")
    sounds.calibrated_sound(zumi)
    time.sleep(2)
    if internet_object["need_to_update"]:
        screen.draw_text_center("I can update")
    time.sleep(1)


@socketio.on('zumi_fail')
def zumi_fail():
    screen.draw_text_center("Failed to connect.\n Try again.")
    zumi.play_note(Note.A5, 100)
    zumi.play_note(Note.F5, 2 * 100)
    time.sleep(2)
    screen.draw_text_center("Go to \"zumidashboard.ai\" in your browser")


@socketio.on('stop_connect_wifi')
def stop_connect_wifi():
    global connect_wifi_thread

    try:
        print('stop connect wifi')
        connect_wifi_thread.raise_exception()
        connect_wifi_thread.join()
    except Exception as e:
        print(e)


@socketio.on('check_internet')
def check_internet(language):
    global check_internet_thread, internet_object

    set_backend_language(language)

    print('check internet')

    internet_object = {
        'language': language,
        'need_to_update': current_app.config['NEED_TO_UPDATE'],
        'checked_internet': current_app.config['CHECKED_INTERNET'],
        'internet_info': current_app.config['INTERNET_INFO']
    }
    check_internet_thread = CheckInternetThread(internet_object)
    check_internet_thread.start()


@socketio.on('check_internet_result')
def check_internet_result():
    global check_internet_thread, internet_object

    try:
        current_app.config['INTERNET_INFO'] = internet_object['internet_info']
    except Exception as e:
        print("network/routes.py - check_internet_result", e)
        socketio.emit('check_internet_result', 'error')
        return

    try:
        if check_internet_thread.is_alive():
            socketio.emit('check_internet_result', 'in_progress')
        else:
            socketio.emit('check_internet_result',
                          current_app.config['INTERNET_INFO'])
    except Exception as e:
        print("network/routes.py - check_internet_result", e)
        socketio.emit('check_internet_result', 'error')


@socketio.on('stop_check_internet')
def stop_check_internet():
    global check_internet_thread

    try:
        print('stop check internet')
        check_internet_thread.raise_exception()
        check_internet_thread.join()
    except Exception as e:
        print(e)


@socketio.on('activate_offline_mode')
def _activate_offline_mode():
    current_app.config['INTERNET_INFO'] = ''
    current_app.config['CHECKED_INTERNET'] = False
    utils.activate_offline_mode()
