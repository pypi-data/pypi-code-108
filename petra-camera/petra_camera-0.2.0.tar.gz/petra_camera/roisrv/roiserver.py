# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------


"""TCP/IP server exposing some summary statistics about the data frame.

"""

import json

import select
import traceback
import time

import logging
import socket

from queue import Queue
from PyQt5 import QtCore

from petra_camera.utils.propagating_thread import ExcThread

from petra_camera.main_window import APP_NAME

logger = logging.getLogger(APP_NAME)

# ----------------------------------------------------------------------
class RoiServer(QtCore.QObject):
    """
    """

    SOCKET_TIMEOUT = .5                            # [s]
    MAX_REQUEST_LEN = 256
    MAX_CLIENT_NUMBER = 32
    CMD_LIST = ["get_sum",]

    # ----------------------------------------------------------------------
    def __init__(self, host, port, cameras_list):

        super(RoiServer, self).__init__()

        self._camera_device = None
        self._cameras_list = None

        self.host = str(host)
        self.port = int(port)

        self._cameras_list = cameras_list

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      # TODO
        self._socket.settimeout(self.SOCKET_TIMEOUT)
        self._socket.bind((self.host, self.port))

        self._connectionMap = []

        self._state = "idle"

        self._errorQueue = Queue()
        self._serverWorker = ExcThread(self.run, 'roiServer', self._errorQueue)
        
        logger.info("ROI server host {}, port {}".format(self.host,
                                                           self.port))

    # ----------------------------------------------------------------------
    def start(self):
        """
        """
        self._serverWorker.start()

    # ----------------------------------------------------------------------
    def run(self):
        """
        """
        self._state = "run"
        self._socket.listen(self.MAX_CLIENT_NUMBER)

        read_list = [self._socket]
        while not self._serverWorker.stopped():
            readable, writable, errored = select.select(read_list, [], [], 0.1)
            for s in readable:
                if s is self._socket:
                    connection, address = self._socket.accept()
                    connection.setblocking(False)
                    self._connectionMap.append([connection, address])
                    logger.info('New client added: {}'.format(address))

            for connection, address in self._connectionMap:
                try:
                    request = connection.recv(self.MAX_REQUEST_LEN).decode()
                    if request:
                        connection.sendall(self._processRequest(request).encode())
                    else:
                        logger.info('Client closed: {}'.format(address))
                        connection.close()
                        self._connectionMap.remove([connection, address])

                except socket.error as err:
                    if err.args[0] == 10035:
                        if self._serverWorker.stopped():
                            break
                    elif err.errno == 11:
                        time.sleep(0.1)
                    elif err.errno == 10054:
                        logger.info('Client closed: {}'.format(address))
                        connection.close()
                        self._connectionMap.remove([connection, address])
                    else:
                        pass

                except KillConnection as _:
                    logger.error(traceback.format_exc())
                    logger.info('Client closed: {}'.format(address))
                    connection.close()
                    self._connectionMap.remove([connection, address])

                except Exception as _:
                    logger.error(traceback.format_exc())
                    break

        self._socket.close()
        self._state = 'aborted'

    # ----------------------------------------------------------------------
    def stop(self):
        """
        """
        self._serverWorker.stop()
        while self._state != 'aborted':
            time.sleep(0.1)

        logger.debug('ROI server stopped')

    # ----------------------------------------------------------------------
    def _processRequest(self, request):
        """
        Returns:
            (str) response, e.g.: "ok;manipulator;x;12.0"
        """
        response = ''
        print(__file__, "processing request '{}'".format(request))

        tokens = request.split()

        try:
            if len(tokens)> 1:
                response = self._make_response("OK", getattr(self, tokens[0])(tokens[1:]))
            else:
                response = self._make_response("OK", getattr(self, tokens[0])())

        except Exception as err:
            response = self._make_response("err", 'request unknown')

        print(__file__, "response '{}'".format(response))

        return response

    # ----------------------------------------------------------------------
    def _make_response(self, flag, message):
        """
        """
        return "{};{}".format(flag, json.dumps(message))

    # ----------------------------------------------------------------------
    def get_list_of_commands(self):

        return self.CMD_LIST

    # ----------------------------------------------------------------------
    def get_sum(self):

        return self._camera_device.get_active_roi_value('sum')

# ----------------------------------------------------------------------
class KillConnection(Exception):
    pass

