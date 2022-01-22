from DecenTT.MQTT.client import Client
from DecenTT.MQTT.logger import logging
from DecenTT.MQTT.logger import logger
from DecenTT.MQTT.MQTTErrors import MQTTValueError
from DecenTT.env.config import SUBSYSTEM_PATH
import threading
import time
import ctypes
import sys

class Publisher:

    def __init__(self, client: Client, topic: str, qos :int = 1,
    log_path:str=f"{SUBSYSTEM_PATH}/runnable.log",
    log_level:str="DEBUG") -> None:
        self.client = client.client
        self.topic = topic
        self.__qos = qos
        self.__pub_val = None
        self.__temp = None
        self.close_runnable = False
        self.thread = None
        self.__log_path = log_path
        self.__log_level = log_level

    def publish(self, payload:any):
        self.client.publish(
            topic = self.topic,
            payload=payload,
            qos= self.__qos
            )


    @property
    def publisherVariable(self):
        return self.__pub_val

    @publisherVariable.setter
    def publisherVariable(self, val):
        if val != self.__pub_val:
            self.client.publish(self.topic, val, qos= self.__qos)
            self.__pub_val = val

    def __thread(self, interval:int):

        while True:

            val_list = ctypes.cast(id(self.__temp), ctypes.py_object).value

            if(len(val_list) == 0):
                raise MQTTValueError
            val = ", ".join(map(str, val_list))

            self.client.publish(self.topic, val, qos= self.__qos)
            logger.debug(f"{val} published")
            if(self.close_runnable): 
                logger.warning("Runnable Closed")
                logger.removeHandler(self.__file_handler)
                sys.exit()

            time.sleep(interval)


    def runnable_publish(self, val:list, interval:int):
        """
            Pass the variable as a non-mutable object
        """
        self.__temp = val


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


        logger.debug(f"runnable publish called")
        self.thread = threading.Thread(target=self.__thread, args=(interval, ))
        logger.debug(f"{self.thread} created")
        self.thread.start()
