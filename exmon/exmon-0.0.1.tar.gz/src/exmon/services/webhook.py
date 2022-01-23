import requests
from exmon.alarm import Alarm
from exmon.exceptions import ServiceExcpetion
from exmon.services import Service


class Webhook(Service):
    """ Webhook Service sends exceptions to a simple webhook """

    # name of the service
    _name: str = 'Webhook'

    def __init__(self, url: str, method: str):
        """Create a new Webhook Service.
        Given a URL to the Webhook it can send exception data to it.

        Args:
            url (:obj:`str`): URL to Webhook.
            method (:obj:`str`): HTTP method that will be used.
                (GET|OPTIONS|HEAD|POST|PUT|PATCH|DELETE)
        """
        self.url = url
        self.method = method

    def __call__(self, alarm: Alarm) -> None:
        """send data to a simple webhook.
        Args:
            alarm (:obj:`Alarm`): data object of the exception.
        """

        data = {
            'error_code': alarm.error_code,
            'exception_name': alarm.get_exc_name(),
            'exception_message': alarm.get_exc_message(),
            'traceback': alarm.get_traceback_list()
        }

        try:
            resp = requests.request(self.method, url=self.url, json=data)
            resp.raise_for_status()
        except Exception as exc:
            raise ServiceExcpetion(self, exc) from exc
