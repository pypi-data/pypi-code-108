# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import dataclasses
import enum
from typing import Optional


class CredentialsMode(enum.Enum):
    login = enum.auto()
    secrets = enum.auto()
    azure = enum.auto()


@dataclasses.dataclass(frozen=True)
class Credentials:
    mode: Optional[CredentialsMode] = None
    name: str = ''

    @classmethod
    def from_dict(cls, data):
        mode = data['mode']
        if mode is not None:
            try:
                mode = CredentialsMode[mode]
            except KeyError:
                mode = None
        return cls(mode=mode, name=data['name'])

    def to_dict(self):
        data = dataclasses.asdict(self)
        mode = data['mode']
        if mode:
            data['mode'] = mode.name
        return data

    def identifier(self):
        return self.name


@dataclasses.dataclass(frozen=True)
class Connection:
    resource: str = ''
    credentials: Credentials = Credentials()

    @classmethod
    def from_dict(cls, data):
        return cls(resource=data['resource'],
                   credentials=Credentials.from_dict(data['credentials']))

    def to_dict(self):
        data = dataclasses.asdict(self)
        data['credentials'] = self.credentials.to_dict()
        return data

    def identifier(self):
        return self.credentials.identifier() or self.resource
