#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#
"""io.py: I/O Classes interfacing with DISCo devices directly.

Contains the base class DiscoIO which must be re-implemented using user-specific read() and write() functions,
dependent on the interface (USB, Serial, Network, etc.).
"""

from discolib.cobs import COBSParser

class Validate:
    """Validation decorators for IO operations."""
    def read(func):
        """Validate input to DiscoIO read"""
        def wrap(*args, **kwargs):           
            data = func(*args, **kwargs)
            return data
        return wrap
    
    def write(func):
        """Validate input to DiscoIO write"""
        def wrap(*args, **kwargs):
            data = args[-1]
            if type(data) is not bytes:
                # TODO: DiscoException (https://gavansystems.atlassian.net/browse/DIS-6)
                raise RuntimeError(f'Cannot write binary data of invalid type: {type(data)}.')
            if len(data) == 0:
                # TODO: DiscoException (https://gavansystems.atlassian.net/browse/DIS-6)
                raise RuntimeError(f'Cannot write empty bytes.')
            return func(*args, **kwargs)
        return wrap
    


class DiscoIO:

    def read_raw(self, *args, **kwargs) -> bytes:
        """Read raw bytes from the component(s). To be implemented (by you!)."""
        raise NotImplementedError('Define your own DiscoIO class that implements read_raw (to 0x00 byte)!')
    
    def write_raw(self, data: bytes, *args, **kwargs) -> None:
        """Send raw bytes to the component(s). To be implemented (by you!)."""
        raise NotImplementedError('Define your own DiscoIO class that implements write_raw(data)!')

    def write(self, data: bytes):
        """Encode and send a message"""
        encoded = COBSParser().encode(data)
        encoded.append(0x00)  # Delimeter byte
        return self.write_raw(bytes(encoded))

    def read(self):
        """Read and validate a response, decoding, and returning the remaining bytes."""
        inbound = self.read_raw()
        decoded = COBSParser().decode(inbound)
        return decoded[:-1]  # TODO: CS
