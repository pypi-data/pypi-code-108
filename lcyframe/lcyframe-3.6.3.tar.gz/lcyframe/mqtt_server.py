# coding=utf-8
from .libs.mqtt_route import MqttTask
from .libs.mqtt_route import ReadMqtt

class MqttWorker(ReadMqtt):
    def __init__(self, **kwargs):
        super(MqttWorker, self).__init__(**kwargs["mqtt_config"])
        self.ROOT = kwargs["ROOT"]
        self.mqtt_config = kwargs["mqtt_config"]
        self.workers_path = self.mqtt_config.get("workers_dir", ["works/mqtt"])
        self.workers = MqttTask.get_workers(self.ROOT, self.workers_path)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    kwargs = {"mqtt_config":
        {
          "host": "localhost",
          "port": 1883,
          "client_id_prefix": "yyq",
          "username": "admin",
          "password": "123456",
          "msg_pwd": 123456

        }
    }
    wk = MqttWorker(**kwargs)
    wk.start()
