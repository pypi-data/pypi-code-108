from flask import Blueprint, current_app
from zumidashboard import socketio, zumi, screen
from zumidashboard.utils import set_backend_language
from zumidashboard.scripts import check_content_missing, shutdown
import zumidashboard.main.utils as utils
import time
import subprocess


main = Blueprint('main', __name__, static_url_path="", static_folder='../dashboard')

@main.route('/')
@main.route('/index')
def index():
    return main.send_static_file('index.html')


@main.route('/main')
def main_page():
    return main.send_static_file('index.html')


@main.route('/learn')
def learn():
    return main.send_static_file('index.html')


@main.route('/explore')
def explore():
    return main.send_static_file('index.html')


@main.route('/zumiterminal-8585677100')
def zumiterminal():
    subprocess.call(['sudo', 'bash',
                    '/usr/local/lib/python3.5/dist-packages/zumidashboard/shell_scripts/jupyter.sh', "/home/pi/Desktop"])
    time.sleep(1)
    while True:
        time.sleep(3)
        p = subprocess.Popen(
            ['sudo', 'bash', '/usr/local/lib/python3.5/dist-packages/zumidashboard/shell_scripts/check_port.sh', '5555'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        p.wait()
        if len(stdout) > 1:
            print('jupyter server is not ready')
        else:
            print('jupyter server is ready')
            break

    return "Jupyter has started. <br><br>" \
           "Please go to <a href=\"http://zumidashboard.ai:5555/terminals/1\">" \
           "http://zumidashboard.ai:5555/terminals/1</a> to access the terminal<br>" \
           "Or go to <a href=\"http://zumidashboard.ai:5555\">http://zumidashboard.ai:5555</a> to access Jupyter"



@socketio.on('disconnect')
def test_disconnect():
    print('Socket disconnected')


@socketio.on('connect')
def test_connect():
    print('a client is connected')
    socketio.emit('language_info')

    if current_app.config['ACTION'] == 'check_internet' or current_app.config['ACTION'] == 'check_last_network':
        time.sleep(1)
        socketio.emit(current_app.config['ACTION'], current_app.config['ACTION_PAYLOAD'])
        current_app.config['ACTION'] = ''
        current_app.config['ACTION_PAYLOAD'] = ''


@main.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@socketio.on('battery_percent')
def battery_percent():
    socketio.emit('battery_percent',str(zumi.get_battery_percent()))


@socketio.on('hardware_info')
def _hardware_info():
    info = utils.hardware_info()
    socketio.emit('hardware_info', info)
    #socketio.emit('battery_percent',str(zumi.get_battery_percent()))


@socketio.on('recalibrate')
def _recalibrate():
    utils.recalibrate()
    socketio.emit("calibrated")
    time.sleep(5)
    utils.screen_hello()


@socketio.on('change_language')
def change_language(language):
    set_backend_language(language)
    check_content = check_content_missing(language)
    time.sleep(1)
    if check_content:
        socketio.emit('check_content_missing', check_content)


@socketio.on('shutdown')
def _shutdown():
    screen.draw_text_center("Please switch off after 15 seconds.")
    shutdown()


@socketio.on('restart')
def restart():
    screen.draw_text_center("Restarting...")
    subprocess.call(["sudo", "systemctl", "restart", "zumidashboard.service"])


@socketio.on('reboot')
def reboot():
    screen.draw_text_center("Reboot")
    subprocess.call(['sudo', 'reboot'])


@socketio.on('view_logs')
def view_logs():
    print('view_logs')
    p = subprocess.Popen('sudo journalctl -u zumidashboard.service > /usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/log.txt',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    p.communicate()
    with open('/usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/log.txt', 'r') as file_data:
        output = ""
        for line in file_data:
            output += line
    socketio.emit('view_logs', output)
