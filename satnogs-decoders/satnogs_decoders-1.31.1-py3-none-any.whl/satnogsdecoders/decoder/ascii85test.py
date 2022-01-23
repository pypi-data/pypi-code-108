# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Ascii85test(KaitaiStruct):
    """:field encoded: textstring.b85encstring.encoded
    :field decoded: b85string.b85decstring.decoded
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_textstring = self._io.read_bytes_term(10, False, True, True)
        _io__raw_textstring = KaitaiStream(BytesIO(self._raw_textstring))
        self.textstring = Ascii85test.B85enc(_io__raw_textstring, self, self._root)
        self._raw_b85string = self._io.read_bytes_term(10, False, True, True)
        _io__raw_b85string = KaitaiStream(BytesIO(self._raw_b85string))
        self.b85string = Ascii85test.B85dec(_io__raw_b85string, self, self._root)

    class B85enc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_b85encstring = self._io.read_bytes_full()
            _process = satnogsdecoders.process.B85encode()
            self._raw_b85encstring = _process.decode(self._raw__raw_b85encstring)
            _io__raw_b85encstring = KaitaiStream(BytesIO(self._raw_b85encstring))
            self.b85encstring = Ascii85test.Base85string(_io__raw_b85encstring, self, self._root)


    class B85dec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_b85decstring = self._io.read_bytes_full()
            _process = satnogsdecoders.process.B85decode()
            self._raw_b85decstring = _process.decode(self._raw__raw_b85decstring)
            _io__raw_b85decstring = KaitaiStream(BytesIO(self._raw_b85decstring))
            self.b85decstring = Ascii85test.Textstring(_io__raw_b85decstring, self, self._root)


    class Base85string(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.encoded = (self._io.read_bytes_full()).decode(u"ASCII")


    class Textstring(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.decoded = (self._io.read_bytes_full()).decode(u"ASCII")



