import ssl
import sys
from typing import Dict, Union

if sys.version_info >= (3, 8):
    from typing import Protocol
else:  # for Python<3.8
    from typing_extensions import Protocol

import httpx


class Client(Protocol):
    @property
    def base_url(self) -> str:
        ...

    @property
    def verify_ssl(self) -> Union[str, bool, ssl.SSLContext]:
        ...

    def get_headers(self) -> Dict[str, str]:
        ...

    def get_cookies(self) -> Dict[str, str]:
        ...

    def get_timeout(self) -> httpx.Timeout:
        ...
