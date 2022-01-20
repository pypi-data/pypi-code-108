import random
import string
from abc import ABC

import websocket

from demessaging.PulsarMessageConstants import PulsarConfigKeys


def get_random_letters(length: int) -> str:
    return "".join(random.choice(string.ascii_letters) for i in range(length))


class PulsarConnection(ABC):
    def __init__(self, pulsar_config):
        self.pulsarConfig = pulsar_config

    def generate_response_topic(self, topic: str = None) -> str:
        topic_name = (
            topic or self.pulsarConfig[PulsarConfigKeys.TOPIC] or "anonymous"
        )

        return topic_name + "_" + get_random_letters(8)

    def open_socket(
        self, subscription: str = None, topic: str = None
    ) -> websocket.WebSocket:
        connection_type = "consumer" if subscription else "producer"
        topic_name = topic or self.pulsarConfig[PulsarConfigKeys.TOPIC]
        sub = ("/" + subscription) if subscription else ""

        topic_url = (
            "ws://"
            + self.pulsarConfig[PulsarConfigKeys.HOST]
            + ":"
            + self.pulsarConfig[PulsarConfigKeys.PORT]
            + "/ws/v2/"
            + connection_type
            + "/"
            + self.pulsarConfig[PulsarConfigKeys.PERSISTENT]
            + "/"
            + self.pulsarConfig[PulsarConfigKeys.TENANT]
            + "/"
            + self.pulsarConfig[PulsarConfigKeys.NAMESPACE]
            + "/"
            + topic_name
            + sub
        )

        sock = websocket.create_connection(topic_url)

        if sock:
            print("connection to {0} established".format(topic_url))

        return sock
