from typing import Any, Dict, Optional, Sequence, Union

from fastel.utils import requests


def format_phone_number(raw: str) -> str:
    pn = ""
    if raw:
        if raw[0] == "0":
            pn = "+886 " + raw[1:]
        elif raw[0] == "+":
            pn = raw
        else:
            pn = "+" + raw
    return pn


class Notifier:
    _stage: str
    _service_url: str
    _service_credentials: str

    def __init__(
        self,
        stage: str,
        client_id: str,
        client_secret: str,
    ):
        self._stage = stage
        self._service_url = (
            "https://notification.revtel-api.com/v4"
            if stage == "prod"
            else "https://notification-stg.revtel-api.com/v4"
        )
        self._service_credentials = (
            f"client_id={client_id}&client_secret={client_secret}"
        )

    def send_sms(self, target: str, title: str, message: str) -> Any:
        """
        Send a sms to target with message
        """

        result = requests.post(
            f"{self._service_url}/sms/send?{self._service_credentials}",
            json={
                "subject": title,  # TODO: check AWS api if subject is used in sms
                "phone": format_phone_number(target),
                "message": message,
            },
        )
        return result.json()

    def send_email(
        self, sender: str, target: Union[str, Sequence[str]], subject: str, html: str
    ) -> Any:
        """
        Send email(s) to target(s) with the subject and html content
        """

        result = requests.post(
            f"{self._service_url}/email/extra/send/{sender}?{self._service_credentials}",
            json={"to": target, "subject": subject, "html": html},
        )
        return result.json()

    def send_template_email(
        self,
        sender: str,
        target: Union[str, Sequence[str]],
        data: Dict[str, Any],
    ) -> Any:
        """
        Send email(s) to target(s) with content built from template using data

        sender: the sender name (`template` is a field in a sender document)
        target: the email(s) you want to send to
        template_data: the dict contains key-value pairs you'd like to pass to the sender's template
        """

        result = requests.post(
            f"{self._service_url}/email/send/{sender}?{self._service_credentials}",
            json={"to": target, "data": data},
        )
        return result.json()

    def push_to_user(
        self,
        user: str,
        subject: str,
        title: str,
        body: str,
        subtitle: Optional[str],
        data: Optional[Dict[str, Any]],
    ) -> Any:
        """
        Send push notifications to a specific user
        """

        result = requests.post(
            f"{self._service_url}/notification/publish/user/{user}?{self._service_credentials}",
            json={
                "subject": subject,
                "title": title,
                "body": body,
                "subtitle": subtitle if subtitle else "",
                "data": data if data else {},
            },
        )
        return result.json()

    def push_to_topic(
        self,
        topic: str,
        subject: str,
        title: str,
        body: str,
        subtitle: Optional[str],
        data: Optional[Dict[str, Any]],
    ) -> Any:
        """
        Send push notifications to all users subscribing a specific topic
        """

        result = requests.post(
            f"{self._service_url}/notification/publish/topic/{topic}?{self._service_credentials}",
            json={
                "subject": subject,
                "title": title,
                "body": body,
                "subtitle": subtitle if subtitle else "",
                "data": data if data else {},
            },
        )
        return result.json()

    def push_to_all(
        self,
        subject: str,
        title: str,
        body: str,
        subtitle: Optional[str],
        data: Optional[Dict[str, Any]],
    ) -> Any:
        """
        Send push notifications to all users
        """

        result = requests.post(
            f"{self._service_url}/notification/publish/topic/public-topic?{self._service_credentials}",
            json={
                "subject": subject,
                "title": title,
                "body": body,
                "subtitle": subtitle if subtitle else "",
                "data": data if data else {},
            },
        )
        return result.json()
