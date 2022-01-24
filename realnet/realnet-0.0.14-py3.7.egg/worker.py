from pynecone import Shell, ProtoCmd
import paho.mqtt.client as mqtt

from .client import Client

class Worker(ProtoCmd, Client):

    def __init__(self):
        self.topic_id = None
        self.function_id = None
        super().__init__('worker',
                         'start realnet worker')

    def add_arguments(self, parser):
        parser.add_argument('topic', help="specifies the id of the topic")
        parser.add_argument('function', help="specifies the id of the function")

    def run(self, args):
        print("Working....")
        self.topic_id = args.topic
        self.function_id = args.function
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.get_url(), 1883, 60)
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.topic_id)

    # The callback function for received message
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))


