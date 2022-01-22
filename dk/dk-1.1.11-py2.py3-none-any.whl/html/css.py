import sys
from dk.collections import pset


class css(pset):
    def __init__(self, **attrs):
        super(css, self).__init__()
        for key, val in sorted(attrs.items()):
            if isinstance(val, bytes):
                val = val.decode('u8')
            if isinstance(key, bytes):
                key = key.decode('u8')
            self[key.replace(u'_', u'-')] = val

    def __setattr__(self, key, val):
        super(css, self).__setattr__(key.replace('_', '-'), val)

    def attrs(self):
        for k, v in sorted(list(self.items())):
            yield k, v

    def _as_bytes(self):
        return self._as_unicode().encode('u8')

    def _as_unicode(self):
        return u';'.join(u'%s:%s' % (k, v) for (k, v) in self.attrs())

    def __str__(self):
        if sys.version_info.major < 3:
            return self._as_bytes()
        else:
            return self._as_unicode()

    __repr__ = __str__
