from deprogressapi import FormalProgressInterface
from demessaging.PulsarMessageConstants import MessageType


class ProgressSendHandler(FormalProgressInterface):
    def __init__(self, pulsar, request_msg, msg_props=None):
        super().__init__()
        self.__pulsar = pulsar
        self.__request_msg = request_msg
        self.msg_props = msg_props

    def send(self, report: str):
        self.__pulsar.send_response(
            request=self.__request_msg,
            msg_type=MessageType.PROGRESS,
            response_payload=report,
            response_properties=self.msg_props
        )
