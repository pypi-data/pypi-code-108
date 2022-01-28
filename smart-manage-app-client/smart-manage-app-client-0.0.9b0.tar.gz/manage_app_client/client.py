import warnings
import time
import datetime
import logging
from typing import Optional
from requests import post, ConnectionError

logger = logging.getLogger('manage_app_client')


def _request(url: str, data: dict, headers: dict) -> bool:
    """Requests helper

    Args:
        url (str): manage system url
        data (dict): event data or exceptio data
        headers (dict): auth headers

    Returns:
        bool: True if success else False
    """
    try:
        r = post(url, json=data, headers=headers)
        if r.status_code > 204:
            warnings.warn(
                f'Invalid response status: {r.status_code}, check Manage app settings'
            )
            return False
        return True
    except ConnectionError as e:
        return False
    except Exception as e:
        return False


class ManageClient(object):
    def __init__(
        self, token: str, system_id: str, system_url: str, debug: bool = False
    ) -> None:
        """Init manage client

        Args:
            token (str): secure token
            system_id (str): system id uuid4
            system_url (str): manage app backend url
            debug (bool, optional): manage deug. Defaults to False.
        """
        self.token = token
        self.system_id = system_id
        self.system_url = self._create_system_url(system_url)
        self.debug = True if int(debug) else False

    def _create_system_url(self, url: str) -> str:
        if not url.endswith("/api/event/"):
            if url.endswith("/"):
                url = f"{url}"
            else:
                url = f"{url}/"
        return url

    def push_event(
        self,
        definition: dict,
        start_time: str,
        status: bool = False,
        description: Optional[str] = None,
    ) -> bool:
        """Push event data

        Args:
            definition (dict): definition of event
            status (bool, optional): finisth status. Defaults to False.

        Returns:
            bool: status
        """

        headers = {"execute-token": self.token}
        name = ', '.join(f'{key}: {value}' for key, value in definition.items())
        if not name:
            return False
        data = {
            "title": name,
            "definition": definition,
            "description": description,
            "is_finish": status,
        }
        if status:
            time.sleep(0.1)
            data["start_time"] = start_time
            data["finish_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            data["start_time"] = start_time
            data["finish_time"] = None
        return _request(
            f'{self.system_url}api/events/?system_id={self.system_id}',
            data=data,
            headers=headers,
        )

    def push_exception(
        self,
        definition: dict,
        description: str,
        start_time: str,
        is_auth: bool = False,
        trb: Optional[str] = None,
    ) -> bool:
        """Push error

        Args:
            definition (str): like {"integration_id": 13, "selection": 2310}
            description (str): ZeroDivizionError
            is_auth (bool, optional): [description]. Defaults to False.
            trb (Optional[str], optional): full traceback. Defaults to None.

        Returns:
            bool: status
        """
        if self.debug:
            logger.debug(trb)
            print(trb)
        else:
            logger.warning(trb)
        exception_url = f'{self.system_url}api/errors/?system_id={self.system_id}'
        name = ', '.join(f'{key}: {value}' for key, value in definition.items())
        headers = {"execute-token": self.token}
        data = {
            "name": name,
            "title": name,
            "description": description,
            "definition": definition,
            "traceback": trb if trb else description,
            "date_time": start_time,
            "is_auth": is_auth,
        }
        _request(exception_url, data=data, headers=headers)
        return True

    def log_exception(
        self,
        definition: dict,
        description: str,
        is_auth: bool = False,
        trb: Optional[str] = None,
    ) -> bool:
        """Puth to errors enpoint

        Args:
            definition (str): event definition
            trb (Optional[str], optional): traceback. Defaults to None.

        Returns:
            bool: status
        """
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.push_event(
            definition=definition, start_time=dt, status=True, description=description,
        )
        if self.debug:
            return False
        return self.push_exception(definition, description, dt, is_auth, trb)
