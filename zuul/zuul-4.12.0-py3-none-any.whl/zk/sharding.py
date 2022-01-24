# Copyright 2020 BMW Group
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import io
from contextlib import suppress
import zlib

from kazoo.exceptions import NoNodeError

# The default size limit for a node in Zookeeper is ~1MiB. However, as this
# also includes the size of the key we can not use all of it for data.
# Because of that we will leave ~47 KiB for the key.
NODE_BYTE_SIZE_LIMIT = 1000000


class RawShardIO(io.RawIOBase):
    def __init__(self, client, path):
        self.client = client
        self.shard_base = path

    def readable(self):
        return True

    def writable(self):
        return True

    def truncate(self, size=None):
        if size != 0:
            raise ValueError("Can only truncate to 0")
        with suppress(NoNodeError):
            self.client.delete(self.shard_base, recursive=True)

    @property
    def _shards(self):
        try:
            return self.client.get_children(self.shard_base)
        except NoNodeError:
            return []

    def _getData(self, path):
        data, _ = self.client.get(path)
        return zlib.decompress(data)

    def readall(self):
        read_buffer = io.BytesIO()
        for shard_name in sorted(self._shards):
            shard_path = "/".join((self.shard_base, shard_name))
            read_buffer.write(self._getData(shard_path))
        return read_buffer.getvalue()

    def write(self, shard_data):
        byte_count = len(shard_data)
        # Only write one key at a time and defer writing the rest to the caller
        shard_bytes = bytes(shard_data[0:NODE_BYTE_SIZE_LIMIT])
        shard_bytes = zlib.compress(shard_bytes)
        if not (len(shard_bytes) < NODE_BYTE_SIZE_LIMIT):
            raise RuntimeError("Shard too large")
        self.client.create(
            "{}/".format(self.shard_base),
            shard_bytes,
            sequence=True,
            makepath=True,
        )
        return min(byte_count, NODE_BYTE_SIZE_LIMIT)


class BufferedShardWriter(io.BufferedWriter):
    def __init__(self, client, path):
        super().__init__(RawShardIO(client, path), NODE_BYTE_SIZE_LIMIT)


class BufferedShardReader(io.BufferedReader):
    def __init__(self, client, path):
        super().__init__(RawShardIO(client, path), NODE_BYTE_SIZE_LIMIT)
