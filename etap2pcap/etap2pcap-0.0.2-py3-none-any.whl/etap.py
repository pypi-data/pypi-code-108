import itertools
import struct

from etap2pcap import common
from etap2pcap import libusb


class Reader:

    def __init__(self,
                 device: libusb.Device,
                 out_endpoint: int = 0x02,
                 in_endpoint: int = 0x06):
        self._device = device
        self._in_endpoint = in_endpoint
        self._buff = b''
        self._size = 0

        device.write(out_endpoint, b'\xaa')
        device.write(out_endpoint, b'\x55')

    def read(self) -> common.Data:
        while True:
            while not self._size and len(self._buff) >= 4:
                size_bytes, self._buff = self._buff[:4], self._buff[4:]
                if (size_bytes == b'\x00\x00\x00\x00' or
                        size_bytes == b'\xff\xff\xff\xff'):
                    continue
                size = struct.unpack('I', size_bytes)[0] & 0xffff
                self._size = size + (4 - (size % 4)) if size % 4 else size

            if not self._size:
                self._buff = b''

            elif self._size <= len(self._buff):
                data, self._buff = (self._buff[:self._size],
                                    self._buff[self._size:])
                self._size = 0
                return data

            data = self._device.read(self._in_endpoint)
            self._buff = memoryview(bytes(itertools.chain(self._buff, data)))
