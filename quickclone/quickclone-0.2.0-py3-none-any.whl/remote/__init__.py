from __future__ import annotations
import typing as t

from .locators import *
from .scp import *


def remote_to_string(remote: UniformResourceLocator, scm: str) -> str:
    if remote.get_scheme() == "ssh" and remote.kwargs.get("explicit_scp"):
        scp_locator = ScpLocator.from_locator(remote)
        if remote.get_username() == "": # Separate if statements for other SCMs.
            if scm == "git":
                scp_locator.username = "git"
        return str(scp_locator)
    else:
        return str(remote)
