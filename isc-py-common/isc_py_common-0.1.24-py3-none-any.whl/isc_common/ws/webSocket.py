import json
import logging
import sys
import traceback

import websocket
from django.conf import settings

from isc_common import setAttr
from isc_common.http.JSONEncoder import JSONEncoder
from isc_common.ws.progressStack import WebSocketExt

logger = logging.getLogger(__name__)


class WebSocket:
    procedures = []
    logger = logging.getLogger(__name__)

    @classmethod
    def recv(cls, **kwrags):
        host = kwrags.get('host')
        logger = kwrags.get('logger')

        if not host:
            raise Exception(f'host is not exists.')

        port = kwrags.get('port')
        if not port:
            raise Exception(f'port not exists.')

        if not isinstance(port, int):
            port = int(port)

        channel = kwrags.get('channel')
        if not channel:
            raise Exception(f'channel is not exists.')

        message = kwrags.get('message')

        if not message:
            raise Exception(f'message is not exists.')

        if not isinstance(message, dict):
            raise Exception(f'message is not dict instance')

        key = 'WebSocket.recv'
        settings.LOCKS.acquire(key)
        try:
            url = f'ws://{host}:{port}/ws/{channel}/'
            ws = websocket.create_connection(url)
            ws.send(json.dumps(message))
            settings.LOCKS.release(key)
            return ws, json.loads(ws.recv())
        except Exception as ex:

            exc_info = sys.exc_info()
            message = str(ex)
            stackTrace = traceback.format_exception(*exc_info)

            logging.error(message)

            for x in stackTrace:
                logger.error(x)

            del exc_info
            settings.LOCKS.release(key)
            return None

    @classmethod
    def send_message(cls, **kwrags):
        host = kwrags.get('host')
        logger = kwrags.get('logger')

        if not host:
            raise Exception(f'host is not exists.')

        port = kwrags.get('port')
        if not port:
            raise Exception(f'port not exists.')

        if not isinstance(port, int):
            port = int(port)

        channel = kwrags.get('channel')
        if not channel:
            raise Exception(f'channel is not exists.')

        message = kwrags.get('message')

        if not isinstance(message, dict):
            if isinstance(message, str):
                message=dict(message=message)
            else:
                raise Exception(f'message is not dict instance')

        try:
            key = 'WebSocket.send_message'
            settings.LOCKS.acquire(key)
            url = f'ws://{host}:{port}/ws/{channel}/'
            ws = websocket.create_connection(url, class_=WebSocketExt)
            ws.send(json.dumps(message, cls=JSONEncoder))
            ws.close()
            settings.LOCKS.release(key)
        except Exception as ex:

            exc_info = sys.exc_info()
            message = str(ex)
            stackTrace = traceback.format_exception(*exc_info)

            logging.error(message)

            for x in stackTrace:
                logger.error(x)

            del exc_info
            settings.LOCKS.release(key)

    @classmethod
    def full_refresh_grid(cls, grid_id):
        WebSocket.send_message(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'application',
            message=dict(type=grid_id),
            logger=logger
        )

    @classmethod
    def row_refresh_grid(cls, grid_id, records):
        if not isinstance(records, list):
            if isinstance(records, dict):
                records = [records]
            else:
                raise Exception(f'records must be list or dict')

        WebSocket.send_message(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'application',
            message=dict(type=grid_id, records=records),
            logger=logger
        )

    @classmethod
    def refresh_progres(cls, grid_id, pk_filed_name, pk_value, progress_field_name, progress_done):

        record = dict()
        setAttr(record, pk_filed_name, pk_value)
        setAttr(record, progress_field_name, progress_done)

        WebSocket.row_refresh_grid(
            grid_id=grid_id,
            records=[record]
        )

    @classmethod
    def send_warning_message(cls, **kwrags):
        setAttr(kwrags, 'type', 'warn')
        WebSocket.send_typing_message(**kwrags)

    @classmethod
    def send_info_message(cls, **kwrags):
        setAttr(kwrags, 'type', 'info')
        WebSocket.send_typing_message(**kwrags)

    @classmethod
    def send_ask_message(cls, **kwrags):
        setAttr(kwrags, 'type', 'ask')
        WebSocket.send_typing_message(**kwrags)

    @classmethod
    def send_typing_message(cls, **kwrags):

        type = kwrags.get('type')
        if not type:
            raise Exception(f'channel is not type.')

        message = kwrags.get('message')
        callbackData = kwrags.get('callbackData')

        if isinstance(message, str):
            message = dict(
                message=message,
                callbackData=callbackData,
                type=type,
            )

        setAttr(kwrags, 'message', message)

        WebSocket.send_message(**kwrags)


def on_message(self, message):
    for proc in self.procedures:
        if hasattr(proc, '__call__'):
            proc(message)


def on_error(self, error):
    self.logger.error(error)


def on_close(self):
    self.logger.debug(f'### closed ###')


def on_open(self):
    self.logger.debug(f'### opened ###')


def remove_proc(self, proc):
    self.procedures.remove(proc)


def append_proc(self, proc):
    self.procedures.append(proc)


def send(self, data):
    if isinstance(data, dict):
        self.webSocket.send(json.dumps(data))
    else:
        raise Exception(f'data is not dict.')


def send_logging(self, msg, type='logging'):
    data = dict(msg=msg, type=type)
    # self.webSocket.send(json.dumps(data))


def __init__(self, **kwargs):
    for k, v in kwargs.items():
        setattr(self, k, v() if callable(v) else v)

    websocket.enableTrace(True)
    self.webSocket = websocket.WebSocketApp(f'ws://{self.host}:{self.port}/ws/{self.channel}/',
                                            on_message=self.on_message,
                                            on_error=self.on_error,
                                            on_close=self.on_close,
                                            on_open=self.on_open
                                            )
    self.webSocket.run_forever()
