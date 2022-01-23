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
Redis DB storage plugin state entities module
"""

# Python base dependencies
import uuid
from abc import ABC
from typing import Dict, List, Optional, Union


class StorageItem(ABC):
    """
    Storage item record

    @package        FastyBird:RedisDbStoragePlugin!
    @module         state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _id: uuid.UUID
    _raw: Dict

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        item_id: uuid.UUID,
        raw: Optional[Dict] = None,
    ) -> None:
        self._id = item_id
        self._raw = {} if raw is None else raw

    # -----------------------------------------------------------------------------

    @property
    def item_id(self) -> uuid.UUID:
        """Item identifier"""
        return self._id

    # -----------------------------------------------------------------------------

    @property
    def raw(self) -> Dict:
        """Stored raw value"""
        return self._raw

    # -----------------------------------------------------------------------------

    @staticmethod
    def create_fields() -> Dict[Union[str, int], Union[str, int, float, bool, None]]:
        """List of fields keys that have to be used when entity is created with optional default value"""
        return {
            0: "id",
        }

    # -----------------------------------------------------------------------------

    @staticmethod
    def update_fields() -> List[str]:
        """List of fields keys that could be edited"""
        return []
