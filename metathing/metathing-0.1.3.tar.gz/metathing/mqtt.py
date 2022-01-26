from paho.mqtt import client as mqtt_client
import random
from pdb import set_trace as stop

class Mqtt():
    def __init__(self, broker: str = 'broker.emqx.io', port: int = 1883) -> None:
        self.broker = broker
        self.port = port
        self.client = None
        self.srv = None

    def connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker: %s:%s!" % (self.broker, self.port))
            else:
                print("Failed to connect, return code %d\n" % rc)

        self.client = mqtt_client.Client(f'python-mqtt-{random.randint(0, 1000)}')
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)
        self.client.loop_start()


    def publish(self, topic: str, content: str, qos:int = 0, retain:bool = False):
        self.client.publish(topic, content, qos, retain)

    # Accept list, e.g. subscribe([("my/topic", 0), ("another/topic", 2)])
    def subscribe(self, topic, qos: int = 1):
        if (isinstance(topic, list)):
            self.client.subscribe(topic)
            for t in topic:
                print("Subscribe to %s" % t)
        else:
            print("Subscribe to %s" % topic)
            self.client.subscribe(topic, qos)

    def unsubscribe(self, topic):
        print("Unsubscribe %s" % topic)
        self.client.unsubscribe(topic)

    def message_callback_add(self, topic: str, callback):
        print("Add callback to topic %s" % topic)
        self.client.message_callback_add(topic, callback)

    def message_callback_remove(self, topic: str):
        print("Remove callback to topic %s" % topic)
        self.client.message_callback_remove(topic)

    def stop(self):
        self.client.loop_stop()