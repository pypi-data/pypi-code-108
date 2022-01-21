from typing import List, Union

from .exceptions import IllegalIndirectionError
from .types import uint8, IntTypes
from .utils import get_size, int_to_bytes, int_from_bytes


class VirtualPointer:
    """Provide virtual pointer operation on bytearray.

    :param source: The source bytearray.
    :param data_type: The type to be operated on.
    :param byteorder: The byte order of source bytearray.
    :param offset: The offset from the start of source bytearray.
    """

    def __init__(
            self,
            source: bytearray,
            data_type: type = uint8,
            byteorder: str = 'little',
            offset: int = 0
    ):
        self.source = source
        self.data_type = data_type
        self.byteorder = byteorder
        self.offset = offset

    def __add__(self, other):
        """Addition Operation."""
        return self.add(int(other))

    def copy(self):
        """Copy object."""
        return VirtualPointer(
            source=self.source,
            data_type=self.data_type,
            byteorder=self.byteorder,
            offset=self.offset
        )

    def add(self, num: int):
        """Offset the pointer position.

        :param num: The number of members on the data type you want to offset.
        :return: New instance.
        """
        new = self.copy()
        new.offset += num * get_size(self.data_type)
        return new

    def cast(self, data_type: type):
        """Cast to the specified type.

        :param data_type: The type to cast.
        :return: New instance.
        """
        new = self.copy()
        new.data_type = data_type
        return new

    def read_bytes(self, size: int) -> bytes:
        """Read bytes from the source bytearray."""
        try:
            return bytes(self.source[self.offset:self.offset + size])
        except IndexError:
            raise IllegalIndirectionError()

    def write_bytes(self, data: Union[bytes, bytearray, List[int]]):
        """Write bytes into the source bytearray."""
        try:
            for i, v in enumerate(data):
                self.source[self.offset + i] = v
        except IndexError:
            raise IllegalIndirectionError()

    def read(self) -> IntTypes:
        """Read an integer from the source bytearray."""
        data = self.read_bytes(get_size(self.data_type))
        return int_from_bytes(data, self.data_type, byteorder=self.byteorder)

    def write(self, value: Union[int, IntTypes]):
        """Write an integer into the source bytearray."""
        data = int_to_bytes(value, self.data_type, byteorder=self.byteorder)
        self.write_bytes(data)
