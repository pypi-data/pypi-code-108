from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_bootstrapper.utils.state import State
from ehelply_microservice_library.integrations.fact import get_fact_endpoint
from pydantic import BaseModel
import json
from fastapi.encoders import jsonable_encoder
from typing import Union, List, Dict, Any, Tuple


class NotificationRelation(BaseModel):
    service: Union[str, None] = None
    product: Union[str, None] = None
    type: Union[str, None] = None
    target: Union[str, None] = None
    link: Union[str, None] = None


class NotificationContent(BaseModel):
    raw: str  # Plain text string. ie. Broadview clinic is delayed by 5 minutes.
    html: Union[
        str, None] = None  # HTML formatted string. ie. <a href="sdfgndgh">Broadview clinic</a> is <strong>delayed</strong> by 5 minutes.


class Notification(BaseModel):
    subject: str
    content: NotificationContent
    relations: List[
        NotificationRelation] = []  # If there is only a single relation, clicking the notification in a UI should take you directly to the relation. If there are multiple, it should take you to a notifications page.
    severity: str = "low"  # low, med, high
    type: str  # ie. ehelply-appointments.appointment.delayed <- used to determine where a notification gets published to
    picture: Union[str, None] = None


class NotificationType(BaseModel):
    email_template: str = "ehelply-generic"
    publisher_types: List[str] = [
        "database"
    ]
    provider_whitelist: Dict[str, List[str]] = {
        "database": [
            "dynamo"
        ]
    }
    type: str


class Notifications(Integration):
    def __init__(self, notification_types: List[NotificationType]) -> None:
        """
        Setup the microservice
        """
        super().__init__("notifications")

        # M2M contains a configured python requests instance which you should use for API requests.
        #  ie. self.m2m.requests
        self.m2m = State.integrations.get("m2m")

        self.notification_types: List[NotificationType] = notification_types

        self.sqs = None

    def init(self):
        """
        STEP 0: Initialize the integration.
        :return:
        """
        super().init()

    def load(self):
        """
        STEP 1: Load the integration
        :return:
        """
        self.sqs = State.aws.make_client("sqs")

        try:
            for notification_type in self.notification_types:
                self.create_type(notification_type)

        except:
            State.logger.warning("Unable to create notification types.")

    @staticmethod
    def get_base_url() -> str:
        """
        Get the base URL of this microservice
        :return:
        """
        return get_fact_endpoint('ehelply-notifications')

    def create_type(self, notification_type: NotificationType):
        response = self.m2m.requests.post(self.get_base_url() + "/types", json={"type": notification_type.dict()})

        return response.json()

    def push_notification(self, notification: Notification):
        queue_url: str = get_fact_endpoint("mq-notifications")
        self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(jsonable_encoder(notification.dict()))
        )
