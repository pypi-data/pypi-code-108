from flask import current_app
import socketio as socketio_client
import subprocess
import time

lib_dir = '/usr/local/lib/python3.5/dist-packages/zumidashboard'

trying_to_open_xterm = False
terminal_mode = ''


def run_terminal_server(mode):
    global trying_to_open_xterm, terminal_mode
    print('run terminal server')

    is_server_running = check_terminal_server_is_running()

    if mode == '/blockly':
        server_type = 'blockly'
    else:
        server_type = 'code_editor'


    print('terminal_mode : ', terminal_mode)
    print('server_type : ', server_type)
    print('is_server_running: ', is_server_running)
    if is_server_running is False and trying_to_open_xterm is False:
        trying_to_open_xterm = True
        terminal_mode = server_type
        print(server_type)
        p = subprocess.run(
            ["python3 /usr/local/lib/python3.5/dist-packages/zumidashboard/pyxtermjs/app.py -m {} & 2>&1".format(server_type)], shell=True)
    elif is_server_running and terminal_mode is not server_type:
        trying_to_open_xterm = False
        subprocess.Popen(['fuser', '-k', '5000/tcp'])
        print('killed')
        time.sleep(1)
        return run_terminal_server(mode)
    return is_server_running


def check_terminal_server_is_running():
    p = subprocess.Popen(
        ['sudo', 'bash', lib_dir + '/shell_scripts/check_port.sh', '5000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    p.wait()
    if len(stdout) > 1:
        print('terminal server is not ready')
        return False
    else:
        print('terminal server is ready')
        if current_app.socketXterm == '':
            connect_to_terminal_server()
        return True


def connect_to_terminal_server():
    current_app.socketXterm = socketio_client.Client()
    current_app.socketXterm.connect(
        "http://localhost:5000", namespaces=['/pty'])
    print('connected to terminal server')

