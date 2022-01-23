import json
import random
from datetime import datetime

import paho.mqtt.client as mqtt
from sdsRayanArvin.Library.LastData import LastData


class Mqtt:
    __client = mqtt.Client()

    def __init__(self):
        Mqtt.__client = mqtt.Client(str(datetime.now()) + str(random.randint(0, 100)))
        Mqtt.__client.on_connect = self.on_connect
        Mqtt.__client.on_message = self.on_message
        Mqtt.__client.connect("mqtt.samacontrol.com", 31512)
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        Mqtt.__client.loop_forever()

    @staticmethod
    def publish(topic, data):
        Mqtt.__client.publish(topic, data, qos=0)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("DEVICE_DATA")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload)
        # LastData().setLastData(message)
