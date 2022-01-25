# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

from ... import Base
from abc import ABC, abstractmethod
from typing import Dict


class ConfigParserBase(ABC, Base):
    @abstractmethod
    def parse(self, content: str) -> Dict:
        """Parse configuration content.

        Method is called in child classes `super().parse(content)` to make sure
        we can implement generic parsing behaviour if necessary.

        :param content: contents of the configuration file to parse
        :type content: str
        :return: the "content" parameter, unchanged
        :rtype: Dict
        """
        return {"content": content}
