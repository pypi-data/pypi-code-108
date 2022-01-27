import errno
import os
import inspect
import json
import mimetypes
import select
import time

try:
    import SocketServer as socketserver
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    import urlparse as parse
except ImportError:
    import socketserver
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib import parse

global __keep_running__
global __credentials_file__
__credentials_file__ = ""

REQUEST_TIMEOUT = 1  # number of seconds we're waiting per request
SESSION_TIMEOUT = 30  # number of seconds we're waiting for user to get credentials

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">

    <title>Please close your browser</title>
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,400i,700|Raleway:300,400" rel="stylesheet">
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootswatch/3.1.1/darkly/bootstrap.min.css">
    <link rel="stylesheet" href="https://id.conductortech.com/css/master.css">
    <link rel="stylesheet" href="https://id.conductortech.com/js/master.js">
    <link rel="stylesheet" href="https://id.conductortech.com/css/main.css">
</head>

<body>
    <div id="header">
        <a href="https://www.conductortech.com">
            <img id="conductorLogo" src="https://id.conductortech.com/img/conductorTech_logo_white.png">
        </a>
    </div>
    <h4 style="display: flex;align-items: center;justify-content: center;flex-direction: column; width: 100%; margin: 30px 0;  align-items: center;">Authenticated successfully</h4>
    <h2 style="display: flex;align-items: center;justify-content: center;flex-direction: column; width: 100%; margin: 30px 0;  align-items: center;">You may now close this window</h2>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, path=""):
        self.send_response(200)
        self.send_header("Content-type", mimetypes.guess_type(path)[0])
        self.end_headers()

    @staticmethod
    def _write_credentials(credentials):
        global __credentials_file__
        if not os.path.exists(os.path.dirname(__credentials_file__)):
            os.makedirs(os.path.dirname(__credentials_file__))
        with open(__credentials_file__, "w") as token_file:
            token_file.write(json.dumps(credentials))

    def do_POST(self):
        self._set_headers()

    def do_GET(self):
        global __keep_running__
        #  Handle arg string
        self._set_headers()
        url_args = parse.parse_qs(parse.urlsplit(self.path).query)

        if "access_token" not in url_args:
            return

        credentials_dict = {
            "access_token": url_args["access_token"][0],
            "token_type": "Bearer",
            "expiration": int(time.time()) + int(url_args["expires_in"][0]),
            "scope": url_args["scope"],
        }
        self._write_credentials(credentials_dict)
        try:
            self.wfile.write(bytes(HTML, encoding="utf8"))
        except:
            self.wfile.write(HTML)

        __keep_running__ = False
        return

    def log_message(self, format, *args):
        return


def retry_loop(server):
    while True:
        try:
            return socketserver.TCPServer.handle_request(server)
        except (OSError, select.error) as e:
            if e.args[0] != errno.EINTR:
                raise


def run(server_class=HTTPServer, handler_class=Handler, port=8085, creds_file=None):
    global __credentials_file__
    global __keep_running__
    __credentials_file__ = creds_file
    __keep_running__ = True

    server_address = ("localhost", port)
    server_class.handle_request = retry_loop
    httpd = server_class(server_address, handler_class)
    httpd.timeout = REQUEST_TIMEOUT
    timeout = time.time() + SESSION_TIMEOUT
    while time.time() < timeout and __keep_running__:
        httpd.handle_request()
