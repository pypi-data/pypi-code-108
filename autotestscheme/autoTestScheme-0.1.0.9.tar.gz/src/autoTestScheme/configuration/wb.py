import json
import logging
import traceback
import zlib
from locust import User, events
import time
import websocket
from ..common import logger
from . import api


class WebSocket(websocket.WebSocket):
    is_locust = False
    is_distinguish_title = False

    def request_success(self, name, response_time: float = 0, request_type: str = "websockt"):
        if self.is_distinguish_title is True:
            name = self.kwargs[1] + '_' + name
        events.request_success.fire(request_type=request_type, name=name, response_time=response_time,
                                    response_length=0)

    def request_failure(self, name, exception, response_time: float = 0, request_type: str = "websockt"):
        if self.is_distinguish_title is True:
            name = self.kwargs[1] + '_' + name
        events.request_failure.fire(request_type=request_type, name=name, response_time=response_time,
                                    response_length=0, exception=exception)

    def connect(self, host, name, timeout=1, header=None):
        self.kwargs = host, name, timeout, header
        if header is None:
            header = {}
        start_time = time.time()
        try:
            self.conn = super().connect(host, header=header, verify_ssl=False, skip_negotiation=False)
            self.settimeout(timeout)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.request_failure("连接", e, response_time=total_time)
            logger.error(traceback.format_exc())
            raise e
        else:
            total_time = int((time.time() - start_time) * 1000)
            logger.debug("websocket建联:url:{},header:{}，用时:{}毫秒".format(host, header, total_time))
            self.request_success("连接", response_time=total_time)

    def reconnect(self):
        self.connect(*self.kwargs)

    def recv_data(self) -> (int, dict):
        """
        获取服务端下发内容， 阻塞形式的，如想不阻塞，请在connect的时候设置超时时间
        :return: 类型，下发内容
        """
        _type, data = super().recv_data()
        if _type == 2:
            data = json.loads(zlib.decompress(data, 16 + zlib.MAX_WBITS))
        else:
            data = json.loads(data)
        logger.debug('---recv---:type:{},{}'.format(_type, data))
        if 'ping' in data:
            self.request_success("ping接收")
        elif 'pong' in data:
            self.request_success("pong接收")
        else:
            self.request_success("其他接收")
        return _type, data

    def send_by_list(self, data: list) -> None:
        """
        发送消息列表
        :param data:
        :return:
        """
        for i in data:
            self.send(i)

    def send(self, msg: dict):
        """
        发送消息
        :param msg:消息
        :return:
        """
        msg = json.dumps(msg)
        start_time = time.time()
        logger.debug('---send---:{}'.format(msg))
        super().send(msg)
        self.request_success("发送消息", response_time=time.time() - start_time)

    def ping(self):
        """
        发送ping请求
        :return:
        """
        msg = {"ping": int(time.time() * 1000)}
        msg = json.dumps(msg)
        logger.debug('---ping---:{}'.format(msg))
        start_time = time.time()
        super().send(msg)
        self.request_success("心跳ping日志", response_time=time.time()-start_time)

    def pong(self):
        """
        发送pong请求
        :return:
        """
        msg = {"pong": int(time.time() * 1000)}
        msg = json.dumps(msg)
        start_time = time.time()
        super().send(msg)
        logger.debug('发送pong请求:{}'.format(msg))
        self.request_success("心跳pong日志", response_time=time.time()-start_time)

    def get_status(self):
        """
        获取状态
        :return:
        """
        super().getstatus()

    def set_status(self, status):
        super().handshake_response.status = status





class webSocket(api.Api):

    def __init__(self, kwargs):
        super().__init__()
        self.kwargs = kwargs

    def get_client(self, api_id, *topics, header=None, **kwargs) -> websocket.WebSocketApp:
        api_data = self.get_api(api_id)
        path = api_data['path']
        url = '{}://{}{}'.format(self.kwargs.get('agreement', 'ws'), self.kwargs['host'], path)
        on_open = kwargs.get('on_open', self.on_open)
        on_error = kwargs.get('on_error', self.on_error)
        on_close = kwargs.get('on_open', self.on_close)
        on_pong = kwargs.get('on_pong', self.on_pong)
        on_ping = kwargs.get('on_ping', self.on_ping)
        on_message = kwargs.get('on_message', self.on_message)
        on_data = kwargs.get('on_data', self.on_data)
        on_cont_message = kwargs.get('on_cont_message')
        ws = websocket.WebSocketApp(url=url, header=header, on_open=on_open, on_error=on_error, on_close=on_close,
                                    on_pong=on_pong, on_ping=on_ping, on_message=on_message)
        ws.topics = topics
        ws.title = api_data['title']
        return ws

    def on_data(self, ws:websocket.WebSocketApp, message, data_type, flag):
        logger.debug("{}内容：{}，类型：{}，flage：{}".format(ws.title, message, data_type, flag))

    def on_close(self, ws:websocket.WebSocketApp, close_status_code, close_msg):
        logger.debug("{}关闭连接,状态码:{}, 关闭消息:{}.....".format(ws.title, close_status_code, close_msg))

    def on_error(self, ws:websocket.WebSocketApp, exception):
        if getattr(a, 'format_exc', None) is not None:
            logger.debug("异常():{}".format(ws.title, exception.format_exc()))
        else:
            logger.exception("异常({})".format(ws.title))

    def on_open(self, ws:websocket.WebSocketApp):
        logger.debug("websocket()连接成功.....".format(ws.title))
        ws.open_start_time = time.time()
        for topic in ws.topics:
            ws.send(json.dumps(topic))

    def on_pong(self, ws:websocket.WebSocketApp, message):
        logger.debug("{}收到pong消息:{}".format(ws.title, message))

    def on_ping(self, ws:websocket.WebSocketApp, message):
        ws.send(json.dumps({"pong": int(time.time() * 1000)}), websocket.ABNF.OPCODE_PONG)
        logger.debug("{}收到ping消息:{}".format(ws.title, message))

    def on_message(self, ws:websocket.WebSocketApp, message):
        logger.debug("{}收到消息:{}".format(ws.title, message))
