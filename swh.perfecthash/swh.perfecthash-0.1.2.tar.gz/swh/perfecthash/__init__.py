# Copyright (C) 2021-2022  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import NewType

from cffi import FFI

from swh.perfecthash._hash_cffi import lib

Key = NewType("Key", bytes)
HashObject = NewType("HashObject", bytes)


class Shard:
    """Low level management for files indexed with a perfect hash table.

    This class allows creating a Read Shard by adding key/object pairs
    and looking up the content of an object when given the key.
    """

    def __init__(self, path: str):
        """Initialize with an existing Read Shard.

        Args:
            path: path to an existing Read Shard file or device

        """
        self.ffi = FFI()
        self.shard = lib.shard_init(path.encode("utf-8"))

    def __del__(self):
        lib.shard_destroy(self.shard)

    @staticmethod
    def key_len():
        return lib.shard_key_len

    def create(self, objects_count: int) -> "Shard":
        """Wipe out the content of the Read Shard. It must be followed by
        **object_count** calls to the **write** method otherwise the content
        of the Read Shard will be inconsistent. When all objects are inserted,
        the Read Shard must be made persistent by calling the **save** method.

        Args:
            objects_count: number of objects in the Read Shard.

        Returns:
            self.

        """
        assert lib.shard_create(self.shard, objects_count) != -1
        return self

    def load(self) -> "Shard":
        """Open the Read Shard file in read-only mode.

        Returns:
            self.
        """
        assert lib.shard_load(self.shard) != -1
        return self

    def save(self) -> int:
        """Create the perfect hash table the **lookup** method
        relies on to find the content of the objects.

        It must be called after **create** and **write** otherwise the
        content of the Read Shard will be inconsistent.

        Returns:
            0 on success, -1 on error.
        """
        return lib.shard_save(self.shard)

    def lookup(self, key: Key) -> HashObject:
        """Fetch the object matching the key in the Read Shard.

        Fetching an object is O(1): one lookup in the index to obtain
        the offset of the object in the Read Shard and one read to get
        the payload.

        Args:
            key: the key associated with the object to retrieve.

        Returns:
           the object as bytes.
        """
        object_size_pointer = self.ffi.new("uint64_t*")
        lib.shard_lookup_object_size(self.shard, key, object_size_pointer)
        object_size = object_size_pointer[0]
        object_pointer = self.ffi.new("char[]", object_size)
        lib.shard_lookup_object(self.shard, object_pointer, object_size)
        return self.ffi.buffer(object_pointer, object_size)

    def write(self, key: Key, object: HashObject) -> int:
        """Add the key/object pair to the Read Shard.

        The **create** method must have been called prior to calling
        the **write** method.

        Args:
            key: the unique key associated with the object.
            object: the object

        Returns:
            0 on success, -1 on error.
        """
        if len(key) != Shard.key_len():
            raise ValueError(f"key length is {len(key)} instead of {Shard.key_len()}")
        return lib.shard_object_write(self.shard, key, object, len(object))
