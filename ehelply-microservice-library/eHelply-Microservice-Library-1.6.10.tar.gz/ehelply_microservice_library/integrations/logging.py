from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_bootstrapper.utils.state import State
from ehelply_microservice_library.integrations.fact import get_fact_endpoint
import json
from fastapi.encoders import jsonable_encoder


class Log(Integration):
    def __init__(self, service: str) -> None:
        super().__init__("log")
        self.sqs = None
        self.service = service

        self.m2m = State.integrations.get("m2m")

    def init(self):
        pass

    def load(self):
        pass

    def post_load(self):
        self.sqs = State.aws.make_client("sqs")

    def _send(self, payload: dict):
        if type(payload['log']['data']) is not dict or type(payload['log']['message']) is not str or type(
                payload['log']['subject']) is not str:
            State.logger.warning('Log entry discarded due to invalid payload.')
            return False

        queue_url = get_fact_endpoint("mq-logging")
        self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(jsonable_encoder(payload))
        )

    def info(self, message: str, subject: str = "", data: dict = None):
        if not data:
            data = {}

        self._send({
            "log": {
                "message": message,
                "severity": "info",
                "subject": subject,
                "data": data
            },
            "service": self.service
        })

    def warning(self, message: str, subject: str = "", data: dict = None):
        if not data:
            data = {}

        self._send({
            "log": {
                "message": message,
                "severity": "warning",
                "subject": subject,
                "data": data
            },
            "service": self.service
        })

    def severe(self, message: str, subject: str = "", data: dict = None):
        if not data:
            data = {}

        self._send({
            "log": {
                "message": message,
                "severity": "severe",
                "subject": subject,
                "data": data
            },
            "service": self.service
        })

    def debug(self, message: str, subject: str = "", data: dict = None):
        if not data:
            data = {}

        self._send({
            "log": {
                "message": message,
                "severity": "debug",
                "subject": subject,
                "data": data
            },
            "service": self.service
        })

    def debugg(self, message: str, subject: str = "", data: dict = None):
        if not data:
            data = {}

        self._send({
            "log": {
                "message": message,
                "severity": "debugg",
                "subject": subject,
                "data": data
            },
            "service": self.service
        })

    def debuggg(self, message: str, subject: str = "", data: dict = None):
        if not data:
            data = {}

        self._send({
            "log": {
                "message": message,
                "severity": "debuggg",
                "subject": subject,
                "data": data
            },
            "service": self.service
        })
