from abc import ABC, abstractmethod
import sys
from typing import Dict

import attr
import pkg_resources

from benchling_api_client.client import Client


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

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints."""
        python_version = ".".join(
            [str(x) for x in (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)]
        )
        try:
            sdk_version = pkg_resources.get_distribution("benchling-sdk").version
        except (pkg_resources.RequirementParseError, TypeError):
            sdk_version = "Unknown"
        return {
            "User-Agent": f"BenchlingSDK/{sdk_version} (Python {python_version})",
            "Authorization": self.auth_method.get_authorization_header(),
        }
