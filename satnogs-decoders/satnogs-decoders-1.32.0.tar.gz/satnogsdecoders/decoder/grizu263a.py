# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Grizu263a(KaitaiStruct):
    """:field teamid: header.teamid
    :field year: header.year
    :field month: header.month
    :field date: header.date
    :field hour: header.hour
    :field minute: header.minute
    :field second: header.second
    :field temp: header.temp
    :field epstoobcina1_current: header.epstoobcina1_current
    :field epstoobcina1_busvoltage: header.epstoobcina1_busvoltage
    :field epsina2_current: header.epsina2_current
    :field epsina2_busvoltage: header.epsina2_busvoltage
    :field baseina3_current: header.baseina3_current
    :field baseina3_busvoltage: header.baseina3_busvoltage
    :field topina4_current: header.topina4_current
    :field topina4_busvoltage: header.topina4_busvoltage
    :field behindantenina5_current: header.behindantenina5_current
    :field behindantenina5_busvoltage: header.behindantenina5_busvoltage
    :field rightsideina6_current: header.rightsideina6_current
    :field rightsideina6_busvoltage: header.rightsideina6_busvoltage
    :field leftsideina7_current: header.leftsideina7_current
    :field leftsideina7_busvoltage: header.leftsideina7_busvoltage
    :field imumx: header.imumx
    :field imumy: header.imumy
    :field imumz: header.imumz
    :field imuax: header.imuax
    :field imuay: header.imuay
    :field imuaz: header.imuaz
    :field imugx: header.imugx
    :field imugy: header.imugy
    :field imugz: header.imugz
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Grizu263a.Header(self._io, self, self._root)

    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pad = self._io.read_bytes(1)
            self.teamid = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.teamid == u"YM2VRZ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.teamid, self._io, u"/types/header/seq/1")
            self.year = self._io.read_u1()
            self.month = self._io.read_u1()
            self.date = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()
            self.temp = self._io.read_s2le()
            self.epstoobcina1_current = self._io.read_u2le()
            self.epstoobcina1_busvoltage = self._io.read_u2le()
            self.epsina2_current = self._io.read_u2le()
            self.epsina2_busvoltage = self._io.read_u2le()
            self.baseina3_current = self._io.read_u2le()
            self.baseina3_busvoltage = self._io.read_u2le()
            self.topina4_current = self._io.read_u2le()
            self.topina4_busvoltage = self._io.read_u2le()
            self.behindantenina5_current = self._io.read_u2le()
            self.behindantenina5_busvoltage = self._io.read_u2le()
            self.rightsideina6_current = self._io.read_u2le()
            self.rightsideina6_busvoltage = self._io.read_u2le()
            self.leftsideina7_current = self._io.read_u2le()
            self.leftsideina7_busvoltage = self._io.read_u2le()
            self.imumx = self._io.read_s2le()
            self.imumy = self._io.read_s2le()
            self.imumz = self._io.read_s2le()
            self.imuax = self._io.read_s2le()
            self.imuay = self._io.read_s2le()
            self.imuaz = self._io.read_s2le()
            self.imugx = self._io.read_s2le()
            self.imugy = self._io.read_s2le()
            self.imugz = self._io.read_s2le()



