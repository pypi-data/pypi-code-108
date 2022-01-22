import os
import struct
import time

from etap2pcap import common


class Writer:

    def __init__(self, path: os.PathLike):
        self._file = open(path, 'a+b')
        self._endians = ''
        self._fraction = 1E6

        try:
            self._file.seek(0)
            header = self._file.read(24)
            if (len(header) == 24 and
                    header[:4] == struct.pack(">I", 0xa1b2c3d4)):
                self._endians = '>'
            elif (len(header) == 24 and
                    header[:4] == struct.pack(">I", 0xa1b23c4d)):
                self._endians = '>'
                self._fraction = 1E9
            elif (len(header) == 24 and
                    header[:4] == struct.pack("<I", 0xa1b2c3d4)):
                self._endians = '<'
            elif (len(header) == 24 and
                    header[:4] == struct.pack("<I", 0xa1b23c4d)):
                self._endians = '<'
                self._fraction = 1E9
            else:
                self._file.seek(0)
                self._file.truncate()
                self._file.write(struct.pack("IHHIIII",
                                             0xa1b2c3d4,
                                             2,
                                             4,
                                             0,
                                             0,
                                             0xffffffff,
                                             1))

            offset = self._file.tell()
            while True:
                header = self._file.read(16)
                if len(header) != 16:
                    break
                packet_size = struct.unpack(f'{self._endians}I',
                                            header[8:12])[0]
                packet = self._file.read(packet_size)
                if len(packet) != packet_size:
                    break
                offset = self._file.tell()

            self._file.seek(offset)
            self._file.truncate()

        except Exception:
            self._file.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self._file is None:
            return
        self._file.close()
        self._file = None

    def write(self, data: common.Data):
        now = time.time()
        self._file.write(struct.pack(f"{self._endians}IIII",
                                     int(now),
                                     int((now - int(now)) * self._fraction),
                                     len(data),
                                     len(data)))
        self._file.write(data)
        self._file.flush()
