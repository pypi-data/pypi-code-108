# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Diy1(KaitaiStruct):
    """:field timestamp: diy1_frame.timestamp
    :field nn1: diy1_frame.nn1
    :field nn2: diy1_frame.nn2
    :field nn3: diy1_frame.nn3
    :field nn4: diy1_frame.nn4
    :field nn5: diy1_frame.nn5
    :field nn6: diy1_frame.nn6
    :field nn7: diy1_frame.nn7
    :field nn8: diy1_frame.nn8
    :field nn9: diy1_frame.nn9
    :field ssb: diy1_frame.ssb
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.diy1_frame = Diy1.Diy1FrameT(self._io, self, self._root)

    class Diy1FrameT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.control = self._io.read_bytes(5)
            self.sentence_init = (self._io.read_bytes(1)).decode(u"ASCII")
            if not self.sentence_init == u"$":
                raise kaitaistruct.ValidationNotEqualError(u"$", self.sentence_init, self._io, u"/types/diy1_frame_t/seq/1")
            self.ts_hh_str = (self._io.read_bytes(2)).decode(u"ASCII")
            self.ts_mm_str = (self._io.read_bytes(2)).decode(u"ASCII")
            self.ts_ss_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn1_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn2_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn3_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn4_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn5_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn6_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn7_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn8_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.nn9_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.ssb_raw = self._io.read_bytes(2)
            self.sentence_end = (self._io.read_bytes(1)).decode(u"ASCII")
            if not self.sentence_end == u"*":
                raise kaitaistruct.ValidationNotEqualError(u"*", self.sentence_end, self._io, u"/types/diy1_frame_t/seq/15")

        @property
        def ssb(self):
            """status bits hex numbers
            bit state                          state
            0     1    = PA Mediam Power         0    = PA High Power (bit 5 = 0) OPERATIVE MODE
            1     1    = ROBOT logger full       0    = logger ROBOT free
            2     1    = ROBOT CALLSIGN change   0    = Robot CALLSIGN not change
            3     1    = ROBOT OP ON             0    = ROBOT OP OFF
            4     1    = logger full             0    = logger empty
            5     1    = PA Low Power            0    = disable  (bit 1 = 0) RECOVERY MODE
            6     1    = RTC setted              0    = RTC no setted
            7     1    = command received        0    = command not received
            """
            if hasattr(self, '_m_ssb'):
                return self._m_ssb if hasattr(self, '_m_ssb') else None

            self._m_ssb = (((KaitaiStream.byte_array_index(self.ssb_raw, 0) - 48) * 16) + (KaitaiStream.byte_array_index(self.ssb_raw, 1) - 48))
            return self._m_ssb if hasattr(self, '_m_ssb') else None

        @property
        def nn1(self):
            """solar charger current [mA]."""
            if hasattr(self, '_m_nn1'):
                return self._m_nn1 if hasattr(self, '_m_nn1') else None

            self._m_nn1 = int(self.nn1_str)
            return self._m_nn1 if hasattr(self, '_m_nn1') else None

        @property
        def nn6(self):
            """RSSI value [dBm]."""
            if hasattr(self, '_m_nn6'):
                return self._m_nn6 if hasattr(self, '_m_nn6') else None

            self._m_nn6 = int(self.nn6_str)
            return self._m_nn6 if hasattr(self, '_m_nn6') else None

        @property
        def nn4(self):
            """transceiver current in TX mode [mA]."""
            if hasattr(self, '_m_nn4'):
                return self._m_nn4 if hasattr(self, '_m_nn4') else None

            self._m_nn4 = int(self.nn4_str)
            return self._m_nn4 if hasattr(self, '_m_nn4') else None

        @property
        def nn5(self):
            """battery voltage [cV]."""
            if hasattr(self, '_m_nn5'):
                return self._m_nn5 if hasattr(self, '_m_nn5') else None

            self._m_nn5 = int(self.nn5_str)
            return self._m_nn5 if hasattr(self, '_m_nn5') else None

        @property
        def nn7(self):
            """OBC temperature [cdegC]."""
            if hasattr(self, '_m_nn7'):
                return self._m_nn7 if hasattr(self, '_m_nn7') else None

            self._m_nn7 = int(self.nn7_str)
            return self._m_nn7 if hasattr(self, '_m_nn7') else None

        @property
        def nn8(self):
            """temperature of transceiver PA [cdegC]."""
            if hasattr(self, '_m_nn8'):
                return self._m_nn8 if hasattr(self, '_m_nn8') else None

            self._m_nn8 = int(self.nn8_str)
            return self._m_nn8 if hasattr(self, '_m_nn8') else None

        @property
        def nn9(self):
            """resets numbers."""
            if hasattr(self, '_m_nn9'):
                return self._m_nn9 if hasattr(self, '_m_nn9') else None

            self._m_nn9 = int(self.nn9_str)
            return self._m_nn9 if hasattr(self, '_m_nn9') else None

        @property
        def timestamp(self):
            """time since last reset (DL4PD: in [s])."""
            if hasattr(self, '_m_timestamp'):
                return self._m_timestamp if hasattr(self, '_m_timestamp') else None

            self._m_timestamp = ((((int(self.ts_hh_str) * 60) * 60) + (int(self.ts_mm_str) * 60)) + int(self.ts_ss_str))
            return self._m_timestamp if hasattr(self, '_m_timestamp') else None

        @property
        def nn2(self):
            """logic current [mA]."""
            if hasattr(self, '_m_nn2'):
                return self._m_nn2 if hasattr(self, '_m_nn2') else None

            self._m_nn2 = int(self.nn2_str)
            return self._m_nn2 if hasattr(self, '_m_nn2') else None

        @property
        def nn3(self):
            """transceiver current in RX mode [mA]."""
            if hasattr(self, '_m_nn3'):
                return self._m_nn3 if hasattr(self, '_m_nn3') else None

            self._m_nn3 = int(self.nn3_str)
            return self._m_nn3 if hasattr(self, '_m_nn3') else None



