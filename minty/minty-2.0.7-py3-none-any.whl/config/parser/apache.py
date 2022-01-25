# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

from .base import ConfigParserBase
from apacheconfig import make_loader  # type: ignore
from threading import BoundedSemaphore
from typing import Any, Dict, cast

max_concurrent_parsers = 1
parser_semaphore = BoundedSemaphore(value=max_concurrent_parsers)


class ApacheConfigParser(ConfigParserBase):
    __slots__ = ["content"]

    def parse(self, content: str) -> dict:
        """Return a dict with the parsed config.

        :return: Parsed configuration
        :rtype: dict
        """
        preparsed_content = super().parse(content)

        if preparsed_content["content"] == "":
            raise ValueError("Cannot parse empty configuration")

        global parser_semaphore
        with make_loader() as loader, parser_semaphore:
            config = cast(Dict[str, Any], loader.loads(content))

        return config
