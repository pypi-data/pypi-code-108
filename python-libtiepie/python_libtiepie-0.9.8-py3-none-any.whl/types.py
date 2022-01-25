from collections import namedtuple
from ctypes import *


Callback = CFUNCTYPE(None, c_void_p)
CallbackDeviceList = CFUNCTYPE(None, c_void_p, c_uint32, c_uint32)
CallbackHandle = CFUNCTYPE(None, c_void_p, c_uint32)
CallbackEvent = CFUNCTYPE(None, c_void_p, c_uint32, c_uint32)


class Tristate(object):  # See: http://stackoverflow.com/a/9504358
    def __init__(self, value=None):
        if any(value is v for v in (True, False, None)):
            self.value = value
        else:
            raise ValueError('Tristate value must be True, False, or None')

    def __eq__(self, other):
        return self.value is other

    def __ne__(self, other):
        return self.value is not other

    def __nonzero__(self):
        raise TypeError('Tristate value may not be used as implicit Boolean')

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Tristate(%s)" % self.value


class Version(namedtuple('Version', ['major', 'minor', 'release', 'build'])):
    def __str__(self):
        return '{0:d}.{1:d}.{2:d}.{3:d}'.format(self.major, self.minor, self.release, self.build)
