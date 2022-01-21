# coding=utf-8
import os
from json import loads, dumps
import logging
import time
from bson.objectid import ObjectId
from traceback import format_exc
from paho.mqtt import client as mqtt, publish as _publish
from lcyframe.libs.crypto import encrypt, decrypt
from lcyframe.libs import utils


class MqttTask(object):
    """订阅队列"""
    _workers = {}

    def __init__(self, topic, qos=2):
        self.topic = topic
        self.qos = qos

    def __call__(self, _handler):
        setattr(_handler, "topic", self.topic)
        setattr(_handler, "qos", self.qos)
        self._workers[_handler.__name__] = _handler
        return _handler

    @classmethod
    def get_workers(cls, ROOT, workers_path):
        if not ROOT:
            raise Exception("the project dir path must been give， and None.")

        if not isinstance(workers_path, list):
            workers_path = [workers_path]

        if workers_path is None:
            raise Exception("mqtt workers_path is not allow empty")

        if not cls._workers:
            for work in workers_path:
                for root, dirs, files in os.walk(utils.fix_path(os.path.join(ROOT, work))):
                    for file in files:
                        if file.startswith("__"):
                            continue
                        if file.endswith(".pyc"):
                            continue
                        if not file.endswith(".py"):
                            continue
                        model_name = root.replace(ROOT, "").lstrip("/").replace("/", ".") + "." + file.rstrip(".py")
                        __import__(model_name, globals(), locals(), [model_name], 0)
                        logging.debug("register mqtt workers [%s.py] success!" % model_name)
        return cls._workers


class ConnectMqtt(object):
    _mqttc = None

    def __init__(self, **config):
        self.mqtt_config = config
        self.mqtt_host = self.mqtt_config.get('host', '127.0.0.1')
        self.mqtt_port = self.mqtt_config.get('port', 1883)
        self.client_id_prefix = self.mqtt_config.get('client_id_prefix', '')
        self.client_id_name = self.mqtt_config.get('client_id_name', str(ObjectId()))
        self.transport = self.mqtt_config.get("transport", "tcp")
        self.keepalive = self.mqtt_config.get("keepalive", 60)

        self.authorization = self.mqtt_config.get("authorization", {})
        self.username = self.authorization.get('username', '')
        self.password = str(self.authorization.get('password', ''))

        self.certificate = self.mqtt_config.get("certificate", {})
        self.cafile = self.certificate.get("cafile")
        self.certfile = self.certificate.get("certfile")
        self.keyfile = self.certificate.get("keyfile")

        self.msg_pwd = str(self.mqtt_config.get('msg_pwd', ''))
        self.encrypt_model = int(self.mqtt_config.get("encrypt_model", 1))

        self.client_role = self.mqtt_config.get("client_role", "producer")    # 链接角色，生产者：producer；消费者：worker
        self.client_id = self.client_id_prefix + self.client_id_name if self.client_id_prefix else self.client_id_name

    @property
    def mqttc(self):
        if ConnectMqtt._mqttc is None:
            _mqttc = mqtt.Client(client_id=self.client_id,
                                 protocol=mqtt.MQTTv311,
                                 transport=self.transport)  # transport="tcp/websockets" 取决于你的配置文件protocol用了那种协议

            pwd = self.mqtt_config.get("authorization", {}).get("use")
            cert = self.mqtt_config.get("certificate", {}).get("use")
            if pwd == cert == True:
                raise Exception("禁止同时开启密码、证书认证")

            if pwd:
                _mqttc.username_pw_set(self.username, password=self.password)

            elif cert:
                _mqttc.tls_set(self.cafile, self.certfile, self.keyfile)

            _mqttc.msg_pwd = self.msg_pwd
            _mqttc.encrypt_model = self.encrypt_model

            _mqttc.connect(self.mqtt_host, self.mqtt_port, self.keepalive)
            if self.client_role == "producer":
                _mqttc.loop_start()
            else:
                # _mqttc.loop_forever()
                pass

            ConnectMqtt._mqttc = _mqttc
        return ConnectMqtt._mqttc


class ReadMqtt(ConnectMqtt):
    """
    消费者：当接收新消息后调用该方法
    """

    def __init__(self, **config):
        super(ReadMqtt, self).__init__(**config)

    def on_log(self, client, obj, level, string):
        """
        实现日志能力
        :param mqttc:
        :param obj:
        :param level:
        :param string:
        :return:
        """
        pass

    def connect(self):
        """

        :return:
        """
        self.mqttc.connect(self.mqtt_host, self.mqtt_port)

    def on_message(self, client, obj, message):
        """
        接收到消息后调用
        message.topic
        message.payload
        message.qos

        :param mqttc:
        :param obj:
        :param msg:
        :return:
        """
        try:
            message = decrypt(message.payload, self.msg_pwd, self.encrypt_model)
        except Exception as e:
            message = message.payload

        try:
            msg = loads(message)
        except Exception as e:
            msg = message

        # msg["client_id"] = client._client_id

        try:
            event = msg.get("event", "")
            topic = msg.get("topic", "")  # "tpoic1","*"
        except:
            logging.warning("message:" + msg)
            logging.warning("event name can not None！")
            return

        for work_name, work in self.workers.items():
            if hasattr(work, event):
                try:
                    logging.debug("时间: %s, topic: %s, event: %s" % (utils.int_to_date_string(utils.now(), "%Y-%m-%d %H:%M:%S"), topic.encode("u8"), event.encode("u8")))

                    if work.topic == topic or work.topic == "#":
                        getattr(work, event)(**msg)
                    else:
                        continue
                except:
                    logging.warning(format_exc())
                    logging.warning(msg)

    def on_connect(self, client, obj, flags, rc):
        """
        订阅topic，连接成功后调用, 支持模糊匹配topic层级
        :param mqttc:
        :param obj:
        :param flags:
        :param rc:
        :return:
        """
        if not self.workers:
            logging.warning("has not work handler.you must load first.")
            return

        topic_list = []
        for name, handler in self.workers.items():
            topic_list.append((getattr(handler, "topic"), getattr(handler, "qos", 2)))

        client.subscribe(topic_list)

        logging.debug("mqtt client connect success. %s" % client._client_id)

    def on_publish(self, client, userdata, mid):
        """
        发送成功后调用
        :param c:
        :param obj:
        :param mid:
        :return:
        """
        logging.debug("mqtt client publish success. %s" % client._client_id)

    def on_disconnect(self, client, userdata, rc):
        """
        客户端断开连接后调用
        :param c:
        :param obj:
        :param mid:
        :return:
        """
        logging.debug("mqtt client disconnect. %s" % client._client_id)

    def publish(self, topic, payload=None, qos=2, retain=False):
        """
        发送消息, 较慢
        :param topic:
        :param payload:
        :param qos:
        :param retain:
        :return:
        """
        if topic is None or len(topic) == 0:
            raise ValueError('Invalid topic.')

        payload = encrypt(payload, self.msg_pwd, self.encrypt_model)
        _publish.single(topic,
                        payload=payload,
                        qos=qos,
                        retain=retain,
                        keepalive=self.keepalive,
                        hostname=self.mqtt_host,
                        port=self.mqtt_port,
                        protocol=mqtt.MQTTv311,
                        auth={'username': self.username, "password": self.password},
                        transport=self.transport
                        )

    def start(self):
        """

        :return:
        """
        self.mqttc.on_message = self.on_message
        self.mqttc.on_log = self.on_log
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.loop_forever()


class WriteMqtt(object):
    """
    生产者：向已订阅的topic里发送消息
    topic, qos 需要在你的业务逻辑里实现赋值
    """

    _mqtt = ConnectMqtt.mqttc

    def __getattr__(self, name):
        if hasattr(self.__class__, '__events__'):
            if name not in self.__class__.__events__:
                raise Exception("Event '%s' is not exists in your Producer Class" % name)

        if name not in self.__dict__:
            if not hasattr(self, "qos"):
                self.qos = 2
            self.__dict__[name] = pub = AgentMqtt(self._mqtt, name, self.topic, self.qos)
            return pub
        else:
            return self.__dict__[name]


class AgentMqtt:
    def __init__(self, mqtt, event, topic, qos=2):
        self.event = event
        self.topic = topic
        self.mqtt = mqtt
        self.qos = qos

    def __repr__(self):
        return "event '%s'" % self.event

    def __call__(self, kwargs):
        payload = {}
        topic = kwargs.get("topic", "")
        qos = kwargs.get("qos", self.qos)
        retain = kwargs.get("retain", False)

        if kwargs:
            payload["event"] = self.event  # message_handler name by Consumer
            payload["topic"] = self.topic  #
            payload["ts"] = utils.now()
            payload.update(kwargs)
        
        payload = encrypt(dumps(payload), self.mqtt.msg_pwd, self.mqtt.encrypt_model) if len(payload) > 1 else None
        self.mqtt.publish(topic or self.topic, payload, int(qos), retain)

