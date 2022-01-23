from http.server import BaseHTTPRequestHandler, HTTPServer
from os import sep, path
from pathlib import Path
import threading
from logging import getLogger
from time import sleep

log = getLogger(__name__)

# HTTPRequestHandler class
class TestHTTPServerRequestHandler(BaseHTTPRequestHandler):
    # GET
    FOLDER, TOTO = path.split(path.realpath(__file__))

    def __init__(self, request, client_address, server):
        # super(BaseHTTPRequestHandler, self).__init__(request, client_address, server)
        super().__init__(request, client_address, server)
        self.path = "index.html"
        self.__folder = ""
        self.__folder, test = path.split(path.realpath(__file__))

    @property
    def folder(self):
        folder_path = Path(__file__)
        return folder_path.parent

    @folder.setter
    def folder(self, folder):
        self.__folder = folder

    def do_GET(self):
        # print(self.folder)
        log.debug(self.path)
        log.debug(super().__getattribute__("path"))
        if self.path == "/":
            self.path = "index.html"
            log.debug("Get root path")

        log.debug(super().__getattribute__("path"))
        try:
            # Check the file extension required and
            # set the right mime type
            send_reply = False
            if self.path.endswith(".html"):
                log.debug("serve html file")
                mimetype = 'text/html'
                send_reply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                send_reply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                send_reply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                send_reply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                send_reply = True
            if self.path == "/close":
                log.debug("close")

            if send_reply:
                # Open the static file requested and send it
                log.debug("current dir is '{}'".format(path.realpath(__file__)))
                log.debug("Before join '{}'".format(self.folder))
                # file_name = "{}{}{}".format(self.folder, sep, self.path)
                file_name = self.folder / self.path.lstrip("/")
                # print(file_name)
                log.debug("Filename '{}'".format(file_name))
                with open(file_name, "br") as f:
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(f.read())
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % file_name)
        except Exception as exception:
            log.error(exception.args[0])


class TestServer:
    def __init__(self):
        self.__server_address = ('0.0.0.0', 8081)
        self.__httpd = HTTPServer(self.__server_address, TestHTTPServerRequestHandler)
        self.__thread = None

    def start(self):
        self.__thread = threading.Thread(target=self.__httpd.serve_forever)
        self.__thread.daemon = True
        self.__thread.start()
        log.debug("Starting server")
        sleep(5)

    def stop(self):
        self.__httpd.shutdown()
        self.__thread = None
        log.debug("Stopping server")
