# Copyright 2020 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Library database handler."""
import os
from redis.sentinel import Sentinel
from .debug import Debug


class Database:
    """ETOS database handler."""

    connected = False
    __database = None
    __reader = None
    __writer = None

    def __init__(self, expire=3600):
        """Load password and host.

        :params expire: How long, in seconds, to persist data keys.
                        Set to None to disable expiration.
        :type expire: int
        """
        self.password = os.getenv("ETOS_DATABASE_PASSWORD")
        self.host = [(Debug().database_host, Debug().database_port)]
        self.expire = expire

    def write(self, key, value):
        """Write a single key to database.

        :param key: Key to write to.
        :type key: str
        :param value: Value to write.
        :type value: any
        :return: Response from redis.
        :rtype: :obj:`redis.Response`
        """
        result = self.writer.set(key, value)
        if self.expire is not None:
            self.writer.expire(key, self.expire)
        return result

    def append(self, key, value):
        """Add a value to key.

        :param key: Key to write to.
        :type key: str
        :param value: Value to write.
        :type value: any
        :return: Response from redis.
        :rtype: :obj:`redis.Response`
        """
        result = self.writer.zadd(key, value)
        if self.expire is not None:
            self.writer.expire(key, self.expire)
        return result

    def read_list(self, key, list_range=(0, -1)):
        """Read a key as list within range.

        :param key: Key to read from.
        :type key: str
        :param list_range: Range of list to return. Defaults to all values.
        :type list_range: tuple
        :return: Value of key.
        :rytpe: any
        """
        return self.reader.zrange(key, *list_range)

    def read(self, key):
        """Read a single key from database.

        :param key: Key to read from.
        :type key: str
        :return: Value of key.
        :rytpe: any
        """
        return self.reader.get(key)

    def remove(self, key):
        """Remove a key from database.

        :param key: Key to remove.
        :type key: str
        :return: Response from redis.
        :rtype: :obj:`redis.Response`
        """
        return self.writer.delete(key)

    @property
    def writer(self):
        """Database writer object."""
        if self.__writer is None:
            self._connect()
            self.__writer = self.__database.master_for("mymaster")
        return self.__writer

    @property
    def reader(self):
        """Database reader object."""
        if self.__reader is None:
            self._connect()
            self.__reader = self.__database.slave_for("mymaster")
        return self.__reader

    def _connect(self):
        """Connect to database."""
        if not self.connected:
            if self.password is None:
                self.__database = Sentinel(self.host)
            else:
                self.__database = Sentinel(
                    self.host,
                    sentinel_kwargs={"password": self.password},
                    password=self.password,
                )
