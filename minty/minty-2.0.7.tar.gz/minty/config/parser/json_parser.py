# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import json
from .base import ConfigParserBase
from typing import Dict


class JSONConfigParser(ConfigParserBase):
    __slots__ = ["content"]

    def parse(self, content: str) -> Dict:
        """Parse JSON file and return dict.

        :param content: content from JSON file
        :type content: str
        :raises ValueError: if content is empty
        :return: parsed config dict
        :rtype: dict
        """
        preparsed_content = super().parse(content)

        if preparsed_content["content"] == "":
            raise ValueError("Cannot parse empty configuration")

        config = json.loads(preparsed_content["content"])

        return config
