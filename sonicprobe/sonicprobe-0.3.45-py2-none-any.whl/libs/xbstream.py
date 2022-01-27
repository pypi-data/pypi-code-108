# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.libs.xbstream"""

import copy
import errno
import gc
import logging
import struct
import sys

LOG = logging.getLogger('xbstream')

XB_STREAM_CHUNK_MAGIC     = 'XBSTCK01'
XB_STREAM_CHUNK_MAGIC_LEN = len(XB_STREAM_CHUNK_MAGIC)

# Magic + flags + type + path len
CHUNK_HEADER_CONSTANT_LEN = XB_STREAM_CHUNK_MAGIC_LEN + 1 + 1 + 4
PATH_LENGTH_OFFSET        = XB_STREAM_CHUNK_MAGIC_LEN + 1 + 1
PATH_LENGTH_OFFSET_END    = PATH_LENGTH_OFFSET + 4
XB_CHUNK_TYPE_EOF         = 'E'
CHUNK_TYPE_OFFSET         = XB_STREAM_CHUNK_MAGIC_LEN + 1
XB_STREAM_MIN_CHUNK_SIZE  = (10 * 1024 * 1024)


class XBStreamDefaultCallbacks(object): # pylint: disable=useless-object-inheritance,too-few-public-methods
    def __init__(self, read = sys.stdin.read, write = sys.stdout.write, tx = None):
        self.read  = read
        self.write = write
        self.tx    = tx


class XBStreamObject(object): # pylint: disable=useless-object-inheritance
    def __init__(self):
        self.buffer         = ""
        self.buffer_size    = 0
        self.filled_size    = 0
        self.tx_size        = 0
        self.chunk_tx       = False
        self.name           = None
        self.name_len       = 0
        self.magic_verified = False
        self.chunk_path_len = 0
        self.chunk_type     = None
        self.payload        = None
        self.payload_size   = 0
        self.chunk_size     = CHUNK_HEADER_CONSTANT_LEN
        self.chunk_no       = 0
        self.tx_started     = False

    def clean(self):
        self.buffer  = ""
        self.payload = None


class XBStreamRead(object): # pylint: disable=useless-object-inheritance
    def __init__(self, callbacks = None, set_payload = False, xb_obj = None):
        self.callbacks        = callbacks or XBStreamDefaultCallbacks()
        self.FILE_CHUNK_COUNT = {} # pylint: disable=invalid-name
        self.EOF              = False # pylint: disable=invalid-name

        if not hasattr(self.callbacks, 'read'):
            raise AttributeError("missing read callback")

        if not hasattr(self.callbacks, 'write'):
            raise AttributeError("missing write callback")

        self.set_payload = set_payload
        self.xb_obj      = xb_obj or XBStreamObject()

    def __call__(self, xb_obj = None):
        if xb_obj:
            self.xb_obj = xb_obj

        if self.xb_obj.chunk_tx:
            self.xb_obj.__init__()

        if self.xb_obj.filled_size < self.xb_obj.chunk_size:
            x = self.callbacks.read(self.xb_obj.chunk_size - self.xb_obj.filled_size)
            if x:
                self.xb_obj.buffer      += x
                self.xb_obj.filled_size += len(x)
                self.buffer_updated()
            else:
                self.EOF = True

        if self.EOF:
            gc.collect()

    def is_streaming(self):
        return not self.EOF

    def reset_chunk_count(self):
        self.FILE_CHUNK_COUNT = {}

    def tx_start(self):
        self.xb_obj.tx_started = True

        if self.xb_obj.filled_size == self.xb_obj.tx_size \
           and self.xb_obj.tx_size < self.xb_obj.chunk_size \
           and not self.EOF:
            x = None
            while True:
                try:
                    x = self.callbacks.read(self.xb_obj.chunk_size - self.xb_obj.filled_size)
                    break
                except IOError as e:
                    if e.errno == errno.EAGAIN:
                        continue

            if x:
                self.xb_obj.buffer      += x
                self.xb_obj.filled_size += len(x)
                self.buffer_updated()
            else:
                self.EOF = True

        real_size = self.xb_obj.filled_size - self.xb_obj.tx_size

        if self.set_payload:
            xlen = 4 + 16 + self.xb_obj.chunk_path_len + CHUNK_HEADER_CONSTANT_LEN
            self.xb_obj.payload = self.xb_obj.buffer[xlen:xlen + self.xb_obj.payload_size]
        else:
            self.xb_obj.payload = None

        if getattr(self.callbacks, 'tx'):
            tx_size = self.callbacks.tx(copy.copy(self.xb_obj))
        else:
            tx_size = self.callbacks.write(self.xb_obj.buffer)

        if tx_size is not None:
            real_size = min([tx_size, self.xb_obj.filled_size - self.xb_obj.tx_size])

        self.xb_obj.tx_size += real_size

        assert(self.xb_obj.filled_size <= self.xb_obj.chunk_size)
        assert(self.xb_obj.tx_size <= self.xb_obj.filled_size)

        if self.xb_obj.tx_size == self.xb_obj.chunk_size:
            self.xb_obj.chunk_tx = True
        else:
            self.tx_start()

        if self.EOF:
            gc.collect()

    def buffer_updated(self):
        ready_for_tx = False

        if not self.xb_obj.magic_verified and self.xb_obj.filled_size >= CHUNK_HEADER_CONSTANT_LEN:
            if self.xb_obj.buffer[0:XB_STREAM_CHUNK_MAGIC_LEN] != XB_STREAM_CHUNK_MAGIC:
                raise ValueError("Error: magic excepted")
            self.xb_obj.magic_verified = True
            self.xb_obj.chunk_path_len = struct.unpack('I', self.xb_obj.buffer[PATH_LENGTH_OFFSET:PATH_LENGTH_OFFSET_END])[0]
            self.xb_obj.chunk_type     = self.xb_obj.buffer[CHUNK_TYPE_OFFSET]
            self.xb_obj.chunk_size     = CHUNK_HEADER_CONSTANT_LEN + self.xb_obj.chunk_path_len
            LOG.debug("buffer updated step 1: "
                      "chunk_path_len: %r, "
                      "chunk_type: %r, "
                      "chunk_size: %r, "
                      "filled_size: %r",
                      self.xb_obj.chunk_path_len,
                      self.xb_obj.chunk_type,
                      self.xb_obj.chunk_size,
                      self.xb_obj.filled_size)

            if self.xb_obj.chunk_type != XB_CHUNK_TYPE_EOF:
                self.xb_obj.chunk_size += 16

        if self.xb_obj.magic_verified \
           and self.xb_obj.payload_size == 0 \
           and self.xb_obj.chunk_type != XB_CHUNK_TYPE_EOF \
           and self.xb_obj.filled_size >= (CHUNK_HEADER_CONSTANT_LEN + self.xb_obj.chunk_path_len + 16):
            payload_len_offset       = CHUNK_HEADER_CONSTANT_LEN + self.xb_obj.chunk_path_len
            payload_len_offset_end   = CHUNK_HEADER_CONSTANT_LEN + self.xb_obj.chunk_path_len + 8
            self.xb_obj.payload_size = struct.unpack('L', self.xb_obj.buffer[payload_len_offset:payload_len_offset_end])[0]
            self.xb_obj.chunk_size   = self.xb_obj.payload_size + 4 + 16 + self.xb_obj.chunk_path_len + CHUNK_HEADER_CONSTANT_LEN
            self.xb_obj.name         = self.xb_obj.buffer[CHUNK_HEADER_CONSTANT_LEN:CHUNK_HEADER_CONSTANT_LEN + self.xb_obj.chunk_path_len]
            LOG.debug("buffer updated step 2: "
                      "name: %r, "
                      "chunk_size: %r, "
                      "payload_size: %r, "
                      "filled_size: %r",
                      self.xb_obj.name,
                      self.xb_obj.chunk_size,
                      self.xb_obj.payload_size,
                      self.xb_obj.filled_size)

        if self.xb_obj.magic_verified \
           and self.xb_obj.chunk_type == XB_CHUNK_TYPE_EOF \
           and self.xb_obj.filled_size >= (CHUNK_HEADER_CONSTANT_LEN + self.xb_obj.chunk_path_len):
            self.xb_obj.name = self.xb_obj.buffer[CHUNK_HEADER_CONSTANT_LEN:CHUNK_HEADER_CONSTANT_LEN + self.xb_obj.chunk_path_len]
            LOG.debug("buffer updated step 3: "
                      "name: %r, "
                      "chunk_size: %r, "
                      "filled_size: %r",
                      self.xb_obj.name,
                      self.xb_obj.chunk_size,
                      self.xb_obj.filled_size)

        if self.xb_obj.filled_size > 0 and self.xb_obj.filled_size == self.xb_obj.chunk_size:
            ready_for_tx = True
            LOG.debug("buffer updated step 4: "
                      "name: %r, "
                      "chunk_size: %r, "
                      "payload_size: %r, "
                      "filled_size: %r",
                      self.xb_obj.name,
                      self.xb_obj.chunk_size,
                      self.xb_obj.payload_size,
                      self.xb_obj.filled_size)

        if not self.xb_obj.tx_started and ready_for_tx:
            if self.xb_obj.name not in self.FILE_CHUNK_COUNT:
                self.FILE_CHUNK_COUNT[self.xb_obj.name] = 0
            self.FILE_CHUNK_COUNT[self.xb_obj.name] += 1
            self.xb_obj.chunk_no = self.FILE_CHUNK_COUNT[self.xb_obj.name]
            LOG.info("ready_for_tx: name: %r, chunk_no: %r, %r", self.xb_obj.name, self.xb_obj.chunk_no, self.xb_obj.chunk_type)
            self.tx_start()


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    xbread = XBStreamRead(set_payload = True)
    try:
        while xbread.is_streaming():
            xbread()
    except KeyboardInterrupt:
        sys.stdout.flush()
    sys.exit(0)
