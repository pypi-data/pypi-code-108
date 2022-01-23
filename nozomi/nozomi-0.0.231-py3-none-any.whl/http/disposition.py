"""
Nozomi
Disposition Module
author: hugh@blinkybeach.com
"""
from nozomi.security.ip_address import IpAddress
from nozomi.http.user_agent import UserAgent
from nozomi.http.accept_language import AcceptLanguage
from nozomi.http.headers import Headers
from nozomi.ancillary.configuration import Configuration
from typing import Optional
from nozomi.ancillary.immutable import Immutable


class Disposition:

    def __init__(
        self,
        headers: Headers,
        configuration: Configuration
    ) -> None:

        self._headers = headers
        self._configuration = configuration

        self._ip_address: Optional[IpAddress] = None
        self._user_agent: Optional[UserAgent] = None
        self._language: Optional[AcceptLanguage] = None

        return

    ip_address = Immutable(lambda s: s._parse_ip_address())
    user_agent = Immutable(lambda s: s._parse_user_agent())
    accept_language = Immutable(lambda s: s._parse_accept_language())

    def _parse_ip_address(self) -> IpAddress:

        if self._ip_address is None:
            self._ip_address = IpAddress.from_headers(
                headers=self._headers,
                boundary_ip_header=self._configuration.boundary_ip_header,
                debug=self._configuration.debug,
                debug_address='127.0.0.1'
            )

        return self._ip_address

    def _parse_user_agent(self) -> UserAgent:

        if self._user_agent is None:
            self._user_agent = UserAgent.from_headers(self._headers)

        return self._user_agent

    def _parse_accept_language(self) -> Optional[AcceptLanguage]:

        if self._language is None:
            self._language = AcceptLanguage.from_headers(self._headers)

        return self._language
