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
Sets of enums for Accounts Module
"""

# Python base dependencies
from enum import Enum, unique

# Library libs
from fastybird_metadata.enum import ExtendedEnum


@unique
class AccountState(ExtendedEnum, Enum):
    """
    Account state type

    @package        FastyBird:Metadata!
    @module         accounts_module

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ACTIVE: str = "active"
    BLOCKED: str = "blocked"
    DELETED: str = "deleted"
    NOT_ACTIVATED: str = "notActivated"
    APPROVAL_WAITING: str = "approvalWaiting"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class IdentityState(ExtendedEnum, Enum):
    """
    Account identity state type

    @package        FastyBird:Metadata!
    @module         accounts_module

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ACTIVE: str = "active"
    BLOCKED: str = "blocked"
    DELETED: str = "deleted"
    INVALID: str = "invalid"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member
