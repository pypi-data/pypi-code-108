"""
This module provides useful functions that facilitate pragmail's routine
operations.
"""
import calendar
import datetime
import json
import platform
import re
import unicodedata
from email import (message_from_binary_file, message_from_bytes,
                   message_from_file, message_from_string)
from email.message import Message
from subprocess import DEVNULL as _DEVNULL
from subprocess import call
from typing import Any, BinaryIO, Optional, TextIO, Union
from urllib.request import urlopen


def date_format(date_ymd: str) -> str:
    """Convert date to IMAP SEARCH Command acceptable format.

    Args:
        date_ymd (str): The date in `YYYY-MM-DD` format.

    Returns:
        str: The date in `DD-MM-YYYY` format and the month replaced with its
            abbreviated form.
    """
    date = date_ymd.split("-")[::-1]
    return f"{date[0]}-{calendar.month_abbr[int(date[1])]}-{date[2]}"


def date_travel(days: int) -> str:
    """Returns the date by day beginning from today.

    Args:
        days (int): Number of days.

    Returns:
        str: The date in `YYYY-MM-DD` format.
    """
    date = datetime.date.today() + datetime.timedelta(days=days)
    return str(date)


def email_domain(email: str) -> str:
    """Get the domain name from the email address.

    Args:
        email (str): The user email address.

    Returns:
        str: The domain name contained in the email.
    """
    return email.split("@")[1].split(".")[0]


def ping_host(host: str) -> bool:
    """Use the system's network utility to check if the server responds to a
    ping request.

    Args:
        host ([type]): IP address of the server or the host name.

    Returns:
        bool: True if host is reachable, False otherwise.
    """
    plat = platform.system().lower()
    c_param = "-n" if plat == "windows" else "-c"
    c_limit = "1"
    t_param = "-w" if plat == "windows" else "-W"
    t_limit = "5000" if plat == "windows" else "5"
    command = [
        "ping",
        c_param,
        c_limit,
        t_param,
        t_limit,
        host,
    ]

    return call(command, stdout=_DEVNULL, stderr=_DEVNULL) == 0


def read_message(
    message: Union[bytes, str, BinaryIO, TextIO],
    as_string: Optional[bool] = False,
) -> Union[str, bytes]:
    """Parse email message.

    Args:
        message (Union[bytes, str, BinaryIO, TextIO]): The message object.
        as_string (Optional[bool[], optional): Parse the message object and
            return a string. Defaults to False.

    Returns:
        Union[str, bytes]: Parsed email message.
    """
    msg: Message = Message()

    if isinstance(message, bytes):
        msg = message_from_bytes(message)
    elif isinstance(message, str):
        msg = message_from_string(message)
    elif isinstance(message, BinaryIO):
        msg = message_from_binary_file(message)
    else:
        msg = message_from_file(message)

    if as_string:
        return msg.as_string()
    return msg.as_bytes()


def sanitize(fname: str) -> str:
    """Sanitize filenames.

    Args:
        fname (str): The original filename.

    Returns:
        str: Fairly safe version of the filename.
    """
    blacklist = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "\0"]
    win_file = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "COM0",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
        "LPT0",
    ]
    fname = "".join(c for c in fname if c not in blacklist)
    fname = "".join(c for c in fname if ord(c) > 31)
    fname = unicodedata.normalize("NFKD", fname)
    fname = fname.rstrip(". ")
    fname = fname.strip()
    fname = "__" if not fname else fname

    if fname in win_file or all((x == "." for x in fname)):
        fname = f"__{fname}"

    if len(fname) > 255:
        parts = re.split(r"/|\\", fname)[-1].split(".")
        if len(parts) > 1:
            ext = f".{parts.pop()}"
            fname = fname[: -len(ext)]
        else:
            ext = ""
        fname = "__" if not fname else fname
        if len(ext) > 254:
            ext = ext[254:]
        maxl = 255 - len(ext)
        fname = fname[:maxl]
        fname = fname + ext
        fname = fname.rstrip(". ")

    return fname


def server_settings(email: str, provider: str) -> dict[str, Any]:
    """Fetch mail server specifications using third party services.

    Args:
        email (str): The user email address.
        provider (str): Service providing email settings lookup.

    Returns:
        dict[str, Any]: Dictionary containing the requested specifications.
    """
    providers = {
        "ES": "https://emailsettings.firetrust.com/settings?q={email}",
    }
    with urlopen(providers[provider].format(email=email)) as res:
        src = list(p if p == provider else "" for p, _ in providers.items())[0]
        return {src: json.loads(res.read())}


def imap_scheme(domain: str) -> tuple[str, str]:
    """Convert domain name to an rfc5092-compliant IMAP URL scheme.

    Args:
        domain (str): Domain name of the service provider.

    Returns:
        tuple[str, str]: The IMAP server URL and its SSL/TLS port number.
    """
    url = f"imap.{domain}.com"
    port = "993"
    return "imap://" + url, port


if __name__ == "__main__":
    pass
