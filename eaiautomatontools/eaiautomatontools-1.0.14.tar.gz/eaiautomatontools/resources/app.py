# -*- Product under GNU GPL v3 -*-
# -*- Author: E.Aivayan -*-
from flask import Flask
import requests
from flask import request
from pathlib import Path
import threading
import logging
import click
log = logging.getLogger('werkzeug')
log.setLevel(logging.FATAL)
log.disabled = True

app = Flask(__name__)

base_path = Path(__file__).parent


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass


def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho


@app.route("/")
def root():
    with open(base_path.joinpath("index.html")) as file:
        return file.read()


@app.route("/favicon.ico")
def fav():
    return "", 200


@app.route("/<path:path>")
def serve_path(path):
    file = base_path.joinpath(path)
    if file.exists():
        with open(file) as f:
            return f.read()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


class Server:
    def __init__(self):
        self.__server = None

    def start(self):
        if self.__server is None:
            self.__server = threading.Thread(target=app.run, kwargs={'port': 8081})
            self.__server.start()

    def stop(self):
        if self.__server is not None:
            response = requests.get("http://localhost:8081/shutdown")
            if response.status_code == 200:
                self.__server = None
            else:
                print("Server not closed")
