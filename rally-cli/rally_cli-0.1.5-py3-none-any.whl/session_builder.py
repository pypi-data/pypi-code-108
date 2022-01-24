from logging import getLogger

import urllib3
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.models import CaseInsensitiveDict

from rallycli.errors.rally_errors import RallyError

## logger definition
logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class SessionBuilder:
    """Class for connectivity to Rally Software API"""

    def __init__(self,
                 key_based_auth: bool = True,
                 external_key: str = None,
                 username: str = None,
                 password: str = None,
                 verify_ssl: bool = True,
                 **kwargs):
        """"""
        logger.debug(f"SessionBuilder**kwargs: {kwargs}")
        self._key_based_auth: bool = key_based_auth
        if key_based_auth and not external_key:
            raise RallyError("Key based auth requires external_key field for API classes creation")
        if not key_based_auth and not (username and password):
            raise RallyError("BasicAuth requires username and password fields for API classes creation")
        headers: dict = {
            "ZSESSIONID": external_key,
            "Content-Type": "application/json"
        }
        self._rally_session: Session = self.__init_rally_session(headers,
                                                                 verify_ssl,
                                                                 kwargs.get("proxies"),
                                                                 username,
                                                                 password)

        logger.info(f"{self.__class__.__name__} python client initialized")

    @staticmethod
    def __init_rally_session(headers: dict, verify_ssl: bool,
                             proxies: dict, username: str, password: str) -> Session:
        rally_session = Session()
        rally_session.headers = CaseInsensitiveDict(headers.items())
        logger.debug("Setting session verify to {}".format(verify_ssl))
        rally_session.verify = verify_ssl
        if username:
            rally_session.auth = HTTPBasicAuth(username, password)
        if proxies:
            rally_session.proxies = CaseInsensitiveDict(proxies.items())
        return rally_session

    def get_session(self) -> Session:
        return self._rally_session
