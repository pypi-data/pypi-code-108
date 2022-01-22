from paho.mqtt import client

from DecenTT.MQTT.MQTTErrors import InvalidCallback
from DecenTT.MQTT.logger import logger


class Client:
    def __init__(
            self,
            host: str,
            port: int = 1883,
            username: str = None,
            password: str = None,
            on_connect=None,
            on_publish=None,
            on_message=None,
            log_path: str = ".",
            **kwargs
    ) -> None:
        self.client = client.Client()

        self.__host = host
        self.__port = port
        self.__uname = username
        self.__pass = password
        self.__on_connect = on_connect if not on_connect is None else None
        self.__on_message = on_message if not on_message is None else self.__int_on_message
        self.__on_publish = on_publish if not on_publish is None else None

        if not self.__on_connect is None:
            self.client.on_connect = self.__on_connect

        if not self.__on_publish is None:
            self.client.on_publish = self.__on_publish

        self.client.on_message = self.__on_message

        # Set username password
        if self.__uname:
            self.client.username_pw_set(username=self.__uname, password=self.__pass)

        # Connect to the Client
        self.client.connect(self.__host, self.__port)

    def __int_on_message(self, client, userdata, msg):
        logger.info(f"{msg.topic} <- {msg.payload}")

    def subscribe(self, topic, callback, **kwargs):
        # check for valid callback
        if not ('function' in str(type(callback))):
            raise InvalidCallback(callback)
        self.client.on_message = callback
        self.client.subscribe(topic=topic, **kwargs)

    def publish(self, topic: str, payload: str, **kwargs):
        self.client.publish(topic=topic, payload=payload, **kwargs)
