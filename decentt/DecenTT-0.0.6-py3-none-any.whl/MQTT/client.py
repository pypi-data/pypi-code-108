import paho.mqtt.client as mqtt
from DecenTT.env.config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS, SUBSYSTEM_PATH
from DecenTT.MQTT.logger import logger, logging
from tqdm import tqdm


class Client:

    """
        Should not inherit the mqtt.Client.
        should provide the wrapped class for mqtt client with logging
        should write logs
    """

    def __init__(
        self,
        host: str = MQTT_HOST,
        port: int = int(MQTT_PORT),
        username: str = MQTT_USER,
        password: str = MQTT_PASS,
        log_path: str = f"{SUBSYSTEM_PATH}/mqtt.log",
        on_connect=None,
        on_message=None,
        on_publish=None,
            **kwargs
    ) -> None:
        self.__log_path = log_path
        client = mqtt.Client()
        client.username_pw_set(username=username, password=password)

        if on_connect == None:
            client.on_connect = self.__on_connect
        else:
            client.on_connect = on_connect

        if on_message == None:
            client.on_message = self.__on_message
        else:
            client.on_message = on_message

        if on_publish == None:
            client.on_publish = self.__on_publish
        else:
            client.on_publish = on_publish

        client.connect(host=host, port=port)
        logger.info(f"Connected to {client}!")
        self.client = client

    def __on_connect(self, client, userdata, flags, rc):
        logger.info(f"connecting to {client}, userdata = {userdata}, flags = {flags}")
        for i in tqdm(range(100)):
            pass
        logger.info(f"Connected to {client}!")

    def __on_message(self, client, userdata, msg):
        logger.debug(f"{msg.topic} got :\t {(msg.payload)}")

    def __on_publish(self, client, userdata, result):
        logger.debug(f"Published! result=\t{result}")

    def get_client(self) -> mqtt.Client:
        return self.client

    def show_logs(self):
        self.client.subscribe("$SYS/#", 1)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.warning(f"Interrupted with KeyBoard")
            self.client.unsubscribe("$SYS/#")

    def write_logs(self, path: str = None, level: str = "DEBUG"):
        if(path == None):
            path = self.__log_path
        file_handler = logging.FileHandler(path)
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "CRITICAL": logging.CRITICAL,
        }
        file_handler.setLevel(level=levels[level])
        logger.addHandler(file_handler)
        self.show_logs()
        logger.removeHandler(file_handler)
