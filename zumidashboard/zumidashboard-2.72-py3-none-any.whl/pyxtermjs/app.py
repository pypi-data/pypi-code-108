#!/usr/bin/env python3
import argparse
from flask import Flask, render_template
from flask_socketio import SocketIO
import socketio as socketio_client
import pty
import os
import time
import subprocess
import select
import termios
import struct
import fcntl
import shlex

__version__ = "0.4.0.2"

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = "secret!"
app.config["fd"] = None
app.config["child_pid"] = None
app.config["mode"] = ""
socketio = SocketIO(app)
socketXterm = socketio_client.Client()


def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_and_forward_pty_output():
    max_read_bytes = 1024 * 20
    socketXterm.connect("http://127.0.0.1")
    while True:
        socketio.sleep(0.01)
        if app.config["fd"]:
            timeout_sec = 0
            (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
            if data_ready:
                output = os.read(app.config["fd"], max_read_bytes).decode()

                if app.config["mode"] == "code_editor":
                    output = output.replace(">>> ", "").replace("... ", "")
                    print('code editor mode output', output)

                    if "show image" in output:
                        try:
                            i = output.split("<")[1].split(">")[0]
                        except:
                            print('error from parsing image number info')
                            i = '1'
                        print('emit socket')
                        socketXterm.emit("show_image", i)

                    if "endfile" in output:
                        socketXterm.emit("endfile", "")
                    else:
                        socketio.emit("pty-output", {"output": output, "mode": app.config["mode"]}, namespace="/pty")

                elif app.config["mode"] == "blockly":
                    if "show image" in output:
                        try:
                            i = output.split("<")[1].split(">")[0]
                        except:
                            print('error from parsing image number info')
                            i = '1'
                        socketXterm.emit("show_image", i)
                        try:
                            output_array = output.split("\n")
                            new_output_array = []
                            for o in output_array:
                                if "show image" not in o:
                                    new_output_array.append(o)
                            output = '\n'.join(new_output_array)
                        except:
                            print('error while removing show image output')

                    if "root@zumi" in output:
                        output = output.split("#")[1].replace(" ", "")

                    if "python3 /home/pi/blockly.py" in output:
                        output = output.split("python3 /home/pi/blockly.py")[1].replace("\n", "")

                    if "clear console" in output:
                        output = output.replace("clear console", "")

                    if "endfile" in output:
                        socketio.emit("pty-output", {"output": output.replace("endfile", ""), "mode": app.config["mode"]}, namespace="/pty")
                        socketXterm.emit("endfile", "")
                    else:
                        socketio.emit("pty-output", {"output": output, "mode": app.config["mode"]}, namespace="/pty")


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    #socketio.emit("pty-output", {"output": 'clear console'}, namespace="/pty")
    if app.config["fd"]:
        app.config["code_editor_input"] = data["input"]

        try:
            if type(data["input"]) == str:
                os.write(app.config["fd"], data["input"].encode())
            else:
                os.write(app.config["fd"], data["input"]["key"].encode())
        except Exception as e:
            print(e)


@socketio.on("resize", namespace="/pty")
def resize(data):
    if app.config["fd"]:
        set_winsize(app.config["fd"], 10, data["cols"])


@socketio.on("connect", namespace="/pty")
def connect():
    """new client connected"""

    if app.config["child_pid"]:
        # already started child process, don't start another
        return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        subprocess.run(app.config["cmd"])
    else:
        # this is the parent process fork.
        # store child fd and pid
        app.config["fd"] = fd
        app.config["child_pid"] = child_pid
        set_winsize(fd, 10, 50)
        cmd = " ".join(shlex.quote(c) for c in app.config["cmd"])
        print("child pid is", child_pid)
        print(
            "starting background task with command `{cmd}` to continously read "
            "and forward pty output to client"
        )
        socketio.start_background_task(target=read_and_forward_pty_output)
        print("task started")
    print('app.py : mode is ', app.config['mode'])
    if app.config["mode"] == "code_editor":
        time.sleep(1)
        os.write(app.config["fd"], "python3\n".encode())
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(
        description=(),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", "--port", default=5000, help="port to run server on")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="host to run server on (use 0.0.0.0 to allow access from other hosts)",
    )
    parser.add_argument("-m", "--mode", default='blockly', help="live printing server mode(blockly/code_editor)")
    parser.add_argument("--debug", action="store_true", help="debug the server")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    parser.add_argument(
        "--command", default="bash", help="Command to run in the terminal"
    )
    parser.add_argument(
        "--cmd-args",
        default="",
        help="arguments to pass to command (i.e. --cmd-args='arg1 arg2 --flag')",
    )
    args = parser.parse_args()
    app.config["mode"] = args.mode
    if args.version:
        print(__version__)
        exit(0)
    print("serving on http://127.0.0.1:{args.port}")
    app.config["cmd"] = [args.command] + shlex.split(args.cmd_args)
    socketio.run(app, debug=args.debug, port=args.port, host=args.host)


if __name__ == "__main__":
    main()
