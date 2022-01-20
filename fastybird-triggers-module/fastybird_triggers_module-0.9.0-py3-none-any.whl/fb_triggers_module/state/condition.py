#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Triggers module condition state module
"""

# Python base dependencies
import uuid
from abc import ABC, abstractmethod


class ConditionState(ABC):
    """
    Condition state

    @package        FastyBird:TriggersModule!
    @module         state/property

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Condition unique identifier"""

    # -----------------------------------------------------------------------------

    @property  # type: ignore[misc]
    @abstractmethod
    def is_fulfilled(self) -> bool:
        """Condition fulfilling status"""

    # -----------------------------------------------------------------------------

    @is_fulfilled.setter  # type: ignore[misc]
    @abstractmethod
    def is_fulfilled(
        self,
        result: bool,
    ) -> None:
        """Condition fulfilling status setter"""
