from typing import Any, Dict
import urllib.parse

import requests
from exmon.alarm import Alarm
from exmon.exceptions import ServiceExcpetion
from exmon.services import Service


class AlertaConfig():
    """Stores configuration data for the alerta service."""

    def __init__(self, **kwargs):

        # either Production or Development
        self.environment = kwargs.get('environment', 'Development')
        # Required resource under alarm
        self.resource = kwargs.get('resource', 'ExampleResource')
        # list of effected services
        self.service = kwargs.get('service', ['example.org'])
        self.origin = kwargs.get('origin', None)
        self.group = kwargs.get('group', None)
        self.status = kwargs.get('status', None)
        self.severity = kwargs.get('severity', None)

    def dict(self, exclude_none: bool = True) -> dict:
        """returns key/value-dict of config.

        Args:
            exclude_none (:obj:`bool`): wether or not None values should be excluded.
        """

        config = self.__dict__
        if exclude_none:
            for (key, value) in list(config.items()):
                if value is None:
                    config.pop(key)
        return config


class Alerta(Service):
    """Alerta Service sends exceptions to an Alerta Server."""

    _name: str = 'Alerta'

    def __init__(self, host_url: str, api_key: str) -> None:
        """Create a new Alerta Service.
        Given a host server it can send exception data to the Alerta API.

        Args:
            host_url (:obj:`str`): URL to Alerta host server.
            api_key (:obj:`str`): Alerta API key.
        """

        # connection data
        self.host_url = str(host_url)
        self.api_key = str(api_key)

        # default config
        self.config = AlertaConfig()

    def __call__(self, alarm: Alarm) -> None:
        """send exception data to Alerta Monitoring system.

        Args:
            alarm (:obj:`Alarm`): data object of the exception.
        """

        # auth
        headers = {'Authorization': f'Key {self.api_key}'}

        # hint: https://docs.alerta.io/api/reference.html#create-an-alert
        data = {
            'event': f'{alarm.get_exc_name()}: {alarm.get_exc_message()}',
            'value': alarm.error_code,
            'text': (
                f'Error Code: {alarm.error_code}. '
                'See raw data for more information.'
            ),
            'rawData': str(alarm.get_formatted_traceback_string()),
        }

        # load data from config and update data dict
        data.update(self.config.dict())

        try:
            # send alert
            resp = requests.post(
                url=urllib.parse.urljoin(self.host_url, '/api/alert'),
                headers=headers,
                json=data
            )
            resp.raise_for_status()
        except Exception as exc:
            raise ServiceExcpetion(self, exc) from exc

    def configure(self, **kwargs: Dict[str, Any]):
        """Configure what data is send to Alerta with each exception alert.

        Args:
            **kwargs (:obj:`Dict[str, Any]`): config arguments.
        """
        self.config = AlertaConfig(**kwargs)
