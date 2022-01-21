"""
This module contains the abstraction that will allow the user to quickly get
started with pragmail. For now, the base features that check for messages in a
specified account on an IMAP mail server can be found here as well.
"""
from imaplib import IMAP4, IMAP4_SSL
from ssl import SSLContext, create_default_context
from typing import Literal, Optional, Union

from pragmail.exceptions import catch_exception
from pragmail.utils import (date_format, date_travel, imap_scheme, ping_host,
                            server_settings)

TEXT_MESSSAGE = "(RFC822)"

_NoResponseData = list[None]
_ResponseData = list[Union[bytes, tuple[bytes, bytes]]]
_AnyResponseData = Union[_NoResponseData, _ResponseData]


class _Client:
    """Client base class."""

    imap4: IMAP4

    @staticmethod
    def fetch_server_settings(user: str) -> str:
        """Fetch mail server settings.

        Args:
            user (str): The user's complete email.

        Raises:
            Exception: If the mail server or its settings cannot be
                identified.

        Returns:
            str: The mail server's URL.
        """
        url: str = ""
        serv = server_settings(user, "ES")
        setts = serv["ES"].get("settings")

        for sett in setts:
            adr = sett.get("address")
            if "imap" in adr:
                url = adr
                break

        return url

    @staticmethod
    def fetch_url_scheme(domain_name: str) -> str:
        """Fetch desired URL scheme.

        Args:
            host (str): The service's domain name.

        Returns:
            str: URL scheme.
        """
        return imap_scheme(domain_name)[0]

    @staticmethod
    def check_connectivity(host: str) -> bool:
        """Check connectivity to host/server.

        Args:
            host (str): The host property of the URL interface.

        Returns:
            bool: True if host is reachable, False otherwise.
        """
        return ping_host(host)

    @staticmethod
    def decode_search_res(uids: list[bytes]) -> list[str]:
        """Convert a list of bytes to a list of string object.

        Args:
            src_uids (list[bytes]): A list of UIDs returned by the IMAP mail
                server.
            dat_uids (list[bytes]): [description]

        Returns:
            tuple[list[str], list[str]]: [description]
        """
        return [str(uid.decode()) for uid in uids]

    @catch_exception
    def login(
        self,
        username: str,
        password: str,
    ) -> tuple[Literal["OK"], list[bytes]]:
        """Identify the client and authenticate the user using plaintext
        password.

        Args:
            username (str): The user's username.
            password (str): The user's password.

        Raises:
            Exception: Raised if username or password was rejected.

        Returns:
            tuple[Literal['OK'], list[bytes]]: Non-specific response.
        """
        return self.imap4.login(username, password)

    @catch_exception
    def logout(self) -> bool:
        """Similar to `IMAP4.logout` but also calls `IMAP4.close`, which
            sends a `CLOSE` command to the server, and is guaranteed to
            almost always work.

        Returns:
            bool: True for success, False otherwise.
        """
        if self.imap4.state == "SELECTED":
            self.imap4.close()

        if self.imap4.state != "LOGOUT":
            self.imap4.logout()

        return True

    @catch_exception
    def select(self, mailbox: str) -> tuple[str, list[Union[bytes, None]]]:
        """Select a mailbox so that messages in the mailbox can be accessed.

        Args:
            mailbox (str): Mailbox name.

        Returns:
            tuple[str, list[Union[bytes, None]]]: The response type and count
                of messages in the specified mailbox.
        """
        return self.imap4.select(mailbox=mailbox, readonly=True)

    @catch_exception
    def latest_message(
        self,
        sender: str,
        date_range: int = -1,
        message_parts: str = TEXT_MESSSAGE,
    ) -> tuple[str, _AnyResponseData]:
        """Convenience method for retrieving the latest message from a
        specified sender.

        Use the largest UID to get the most recent message. Since the search
        key `ON` command cannot guarantee a result, this method uses
        `SENTSINCE` and the days prior today —represented by negative
        integers.

        Args:
            sender (str): String contained in the envelope structure's FROM
                field.
            date_range (int, optional): Time frame or days in which a message
                is expected to be present. Defaults to -1.
            message_parts (str, optional): Message data item names. Defaults
                to TEXT_MESSSAGE (RFC822/BODY[]).

        Raises:
            Exception: Raised when date_range is greater than -1.
            Exception: No message was found from specified sender.

        Returns:
            tuple[str, _AnyResponseData]: IMAP response type and the message
                data.
        """
        if date_range > -1:
            raise Exception(
                f"date_range can't be greater than -1: \
                {date_range}"
            )

        latest_uid = 0
        sentsince = date_format(date_travel(date_range))
        src = self.decode_search_res(
            self.imap4.search(None, f'(FROM "{sender}")')[1],
        )
        dat = self.decode_search_res(
            self.imap4.search(None, f"(SENTSINCE {sentsince})")[1],
        )

        for uid in dat[0].split(" "):
            _uid = int(uid)
            if uid in src[0].split(" "):
                # Since UIDs are incremented, its length is relative to
                # the message's freshness; the larger the UID, the more
                # recent the message.
                if _uid > latest_uid:
                    latest_uid = _uid

        if latest_uid > 0:
            return self.imap4.fetch(str(latest_uid), message_parts)

        raise Exception(f"Message not found: {latest_uid}")

    @catch_exception
    def __enter__(self):
        return self

    @catch_exception
    def __exit__(self, exc_type: str, exc_value: str, trace: str):
        self.logout()

        if exc_type:
            print(f"exc_type: {exc_type}")
            print(f"exc_value: {exc_value}")
            print(f"exc_traceback: {trace}")


class Client(_Client):
    """Readonly client connection to mail server.

    Based on `imaplib.IMAP4`, allowing a certain degree of user flexibility.

    For more information and further usage, visit:
    - https://docs.python.org/3/library/imaplib.html
    - https://datatracker.ietf.org/doc/html/rfc2060.html
    """

    def __init__(
        self,
        host: str,
        port: int = 993,
        ssl_context: Optional[SSLContext] = None,
        timeout: float = 5.0,
    ) -> None:
        """
        Args:
            host (str): The service's domain name, IMAP server URL or user
                email.
            port (int, optional): IMAP port (e.g. 143). Defaults to 993.
            ssl_context (Optional[SSLContext], optional): Client SSL Context.
                If `None`, pragmail uses `ssl.create_default_context`
            timeout (float, optional): Connection timeout. Defaults to 5.0.
        """
        if "@" in host:
            host = self.fetch_server_settings(host).replace("imap://", "")
        elif "imap" not in host:
            host = self.fetch_url_scheme(host).replace("imap://", "")
            if not self.check_connectivity(host):
                raise Exception("Name or service not known.")

        if port == 993:
            ssl_context = create_default_context()

        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.timeout = timeout

        if self.ssl_context is not None:
            self.imap4 = IMAP4_SSL(
                host=host,
                port=port,
                ssl_context=ssl_context,
                timeout=timeout,
            )
        else:
            self.imap4 = IMAP4(
                host=host,
                port=port,
                timeout=timeout,
            )

    def __repr__(self) -> str:
        class_repr = (
            "Client(host={host}, port={port}, "
            "ssl_context={ssl_context}, timeout={timeout}"
        )

        return class_repr.format(
            host=self.host,
            port=self.port,
            ssl_context=self.ssl_context,
            timeout=self.timeout,
        )


ResponseData = _ResponseData
