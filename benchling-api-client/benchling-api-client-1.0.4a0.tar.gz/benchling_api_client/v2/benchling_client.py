from abc import ABC, abstractmethod
import sys
from typing import Dict

import attr
import pkg_resources

from benchling_api_client.v2.client import Client


class AuthorizationMethod(ABC):
    """An abstract class that defines how the Benchling Client will authorize with the server."""

    @abstractmethod
    def get_authorization_header(self) -> str:
        """
        Return a string that will be passed to the HTTP Authorization request header.

        The returned string is expected to contain both the scheme (e.g. Basic, Bearer) and parameters.
        """


@attr.s(auto_attribs=True)
class BenchlingApiClient(Client):
    auth_method: AuthorizationMethod
    _package: str = attr.ib(init=False, default="benchling-api-client")
    _user_agent: str = attr.ib(init=False, default="BenchlingAPIClient")

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints."""
        python_version = ".".join(
            [str(x) for x in (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)]
        )
        try:
            api_client_version = pkg_resources.get_distribution(self._package).version
        except (pkg_resources.DistributionNotFound, pkg_resources.RequirementParseError, TypeError):
            api_client_version = "Unknown"
        return {
            "User-Agent": f"{self._user_agent}/{api_client_version} (Python {python_version})",
            "Authorization": self.auth_method.get_authorization_header(),
        }
