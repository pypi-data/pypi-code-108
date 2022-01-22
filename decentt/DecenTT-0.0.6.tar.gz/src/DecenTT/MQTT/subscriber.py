from DecenTT.MQTT.client import Client
from DecenTT.MQTT.logger import logging, logger
from DecenTT.env.config import SUBSYSTEM_PATH


class Subscriber:
    def __init__(self, client:Client, topic:any, callback:any = None, qos:int = 1, log_path:str = f"{SUBSYSTEM_PATH}/subscriber.log", log_level:str="DEBUG") -> None:
        self.__client = client.client
        if(not(callback == None)):
            self.__client.on_message = callback
        else:
            self.__client.on_message = self.__callback
        self.__client.subscribe(topic=topic, qos=qos)

        self.__log_path = log_path
        self.__log_level = log_level
        self.__file_handler = logging.FileHandler(self.__log_path)
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "CRITICAL": logging.CRITICAL,
        }
        self.__file_handler.setLevel(level=levels[self.__log_level])
        logger.addHandler(self.__file_handler)

    def __callback(self, client, userdata, msg):
        logger.debug(f"From {client}:\t {msg.topic} got :\t {(msg.payload)}")

    def stop_logging(self):
        logger.removeHandler(self.__file_handler)

