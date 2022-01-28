# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Polyitan1(KaitaiStruct):
    """:field dst_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field data_type: ax25_frame.payload.ax25_info.header.data_type
    :field beacon0: ax25_frame.payload.ax25_info.data.body
    :field device_err1_raw: ax25_frame.payload.ax25_info.data.device_err1_raw
    :field device_err2_raw: ax25_frame.payload.ax25_info.data.device_err2_raw
    :field device_err3_raw: ax25_frame.payload.ax25_info.data.device_err3_raw
    :field ss256: ax25_frame.payload.ax25_info.data.ss256
    :field rtc_s: ax25_frame.payload.ax25_info.data.rtc_s
    :field sat_mode: ax25_frame.payload.ax25_info.data.sat_mode
    :field submode: ax25_frame.payload.ax25_info.data.submode
    :field mux_i3_3: ax25_frame.payload.ax25_info.data.mux_i3_3
    :field arege: ax25_frame.payload.ax25_info.data.arege
    :field eab1: ax25_frame.payload.ax25_info.data.eab1
    :field eab2: ax25_frame.payload.ax25_info.data.eab2
    :field eab3: ax25_frame.payload.ax25_info.data.eab3
    :field v_acb: ax25_frame.payload.ax25_info.data.v_acb
    :field cab1: ax25_frame.payload.ax25_info.data.cab1
    :field cab2: ax25_frame.payload.ax25_info.data.cab2
    :field cab3: ax25_frame.payload.ax25_info.data.cab3
    :field c_from_sb_all: ax25_frame.payload.ax25_info.data.c_from_sb_all
    :field curr_sp_main: ax25_frame.payload.ax25_info.data.curr_sp_main
    :field c_load_all: ax25_frame.payload.ax25_info.data.c_load_all
    :field p_sbx: ax25_frame.payload.ax25_info.data.p_sbx
    :field p_sby: ax25_frame.payload.ax25_info.data.p_sby
    :field p_sbz: ax25_frame.payload.ax25_info.data.p_sbz
    :field device_errors: ax25_frame.payload.ax25_info.data.device_errors
    :field magtl_x: ax25_frame.payload.ax25_info.data.magtl_x
    :field magtl_y: ax25_frame.payload.ax25_info.data.magtl_y
    :field magtl_z: ax25_frame.payload.ax25_info.data.magtl_z
    :field gyro_x_mdps: ax25_frame.payload.ax25_info.data.gyro_x_mdps
    :field gyro_y_mdps: ax25_frame.payload.ax25_info.data.gyro_y_mdps
    :field gyro_z_mdps: ax25_frame.payload.ax25_info.data.gyro_z_mdps
    :field mux_i5_0: ax25_frame.payload.ax25_info.data.mux_i5_0
    :field ads1248_tmp_c: ax25_frame.payload.ax25_info.data.ads1248_tmp_c
    :field charge: ax25_frame.payload.ax25_info.data.charge
    :field antennas_status: ax25_frame.payload.ax25_info.data.antennas_status
    :field t_ab1: ax25_frame.payload.ax25_info.data.t_ab1
    :field t_ab2: ax25_frame.payload.ax25_info.data.t_ab2
    :field t_ab3: ax25_frame.payload.ax25_info.data.t_ab3
    :field mode: ax25_frame.payload.ax25_info.data.mode
    :field device_status: ax25_frame.payload.ax25_info.info.data.device_status
    :field rtc_ss: ax25_frame.payload.ax25_info.data.rtc_ss
    :field u_3_3v_digi: ax25_frame.payload.ax25_info.data.u_3_3v_digi
    :field u_3_3v_rf: ax25_frame.payload.ax25_info.data.u_3_3v_rf
    :field u_3_3v_rf_amp: ax25_frame.payload.ax25_info.data.u_3_3v_rf_amp
    :field temp2: ax25_frame.payload.ax25_info.data.temp2
    :field temp1: ax25_frame.payload.ax25_info.data.temp1
    
    .. seealso::
       Source - https://amsat.vhfdx.in.ua/documents/polyitan.ksy
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Polyitan1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Polyitan1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Polyitan1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Polyitan1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Polyitan1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Polyitan1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Polyitan1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Polyitan1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Polyitan1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Polyitan1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Polyitan1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Polyitan1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self._parent.ax25_header.src_callsign_raw.callsign_ror.callsign
            if _on == u"EM0UKP":
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Polyitan1.Ax25Info(_io__raw_ax25_info, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Beacon1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.device_err1_raw = self._io.read_u1()
            self.device_err2_raw = self._io.read_u1()
            self.device_err3_raw = self._io.read_u1()
            self.ss256 = self._io.read_u1()
            self.rtc_s = self._io.read_s4le()
            self.sat_mode = self._io.read_u1()
            self.submode = self._io.read_u1()
            self.magtl_x1_raw = self._io.read_u1()
            self.magtl_x2_raw = self._io.read_u1()
            self.magtl_x3_raw = self._io.read_u1()
            self.magtl_y1_raw = self._io.read_u1()
            self.magtl_y2_raw = self._io.read_u1()
            self.magtl_y3_raw = self._io.read_u1()
            self.magtl_z1_raw = self._io.read_u1()
            self.magtl_z2_raw = self._io.read_u1()
            self.magtl_z3_raw = self._io.read_u1()
            self.gyro_x1_mdps_raw = self._io.read_u1()
            self.gyro_x2_mdps_raw = self._io.read_u1()
            self.gyro_x3_mdps_raw = self._io.read_u1()
            self.gyro_y1_mdps_raw = self._io.read_u1()
            self.gyro_y2_mdps_raw = self._io.read_u1()
            self.gyro_y3_mdps_raw = self._io.read_u1()
            self.gyro_z1_mdps_raw = self._io.read_u1()
            self.gyro_z2_mdps_raw = self._io.read_u1()
            self.gyro_z3_mdps_raw = self._io.read_u1()
            self.mux_i3_3 = self._io.read_u2le()
            self.mux_i5_0_raw = self._io.read_u2le()
            self.ads1248_tmp_c_raw = self._io.read_s2le()
            self.arege = self._io.read_u2le()
            self.antennas_status_raw = self._io.read_u2le()
            self.charge_raw = self._io.read_u2be()
            self.eab1 = self._io.read_u2le()
            self.eab2 = self._io.read_u2le()
            self.eab3 = self._io.read_u2le()
            self.v_acb = self._io.read_s2le()
            self.cab1 = self._io.read_s2le()
            self.cab2 = self._io.read_s2le()
            self.cab3 = self._io.read_s2le()
            self.c_from_sb_all = self._io.read_s2le()
            self.curr_sp_main = self._io.read_u2le()
            self.c_load_all = self._io.read_s2le()
            self.t_ab2_raw = self._io.read_s2le()
            self.t_ab3_raw = self._io.read_s2le()
            self.p_sbx = self._io.read_s2le()
            self.p_sby = self._io.read_s2le()
            self.p_sbz = self._io.read_s2le()

        @property
        def device_errors(self):
            """non zero if orientation enabled."""
            if hasattr(self, '_m_device_errors'):
                return self._m_device_errors if hasattr(self, '_m_device_errors') else None

            self._m_device_errors = (((self.device_err3_raw << 16) | (self.device_err2_raw << 8)) | self.device_err1_raw)
            return self._m_device_errors if hasattr(self, '_m_device_errors') else None

        @property
        def charge(self):
            if hasattr(self, '_m_charge'):
                return self._m_charge if hasattr(self, '_m_charge') else None

            self._m_charge = (self.charge_raw * 0.1)
            return self._m_charge if hasattr(self, '_m_charge') else None

        @property
        def magtl_y(self):
            """non zero if orientation enabled."""
            if hasattr(self, '_m_magtl_y'):
                return self._m_magtl_y if hasattr(self, '_m_magtl_y') else None

            self._m_magtl_y = (((self.magtl_y3_raw << 16) | (self.magtl_y2_raw << 8)) | self.magtl_y1_raw)
            return self._m_magtl_y if hasattr(self, '_m_magtl_y') else None

        @property
        def t_ab3(self):
            if hasattr(self, '_m_t_ab3'):
                return self._m_t_ab3 if hasattr(self, '_m_t_ab3') else None

            self._m_t_ab3 = (self.t_ab3_raw * 0.1)
            return self._m_t_ab3 if hasattr(self, '_m_t_ab3') else None

        @property
        def ads1248_tmp_c(self):
            if hasattr(self, '_m_ads1248_tmp_c'):
                return self._m_ads1248_tmp_c if hasattr(self, '_m_ads1248_tmp_c') else None

            self._m_ads1248_tmp_c = (self.ads1248_tmp_c_raw * 0.1)
            return self._m_ads1248_tmp_c if hasattr(self, '_m_ads1248_tmp_c') else None

        @property
        def magtl_z(self):
            """non zero if orientation enabled."""
            if hasattr(self, '_m_magtl_z'):
                return self._m_magtl_z if hasattr(self, '_m_magtl_z') else None

            self._m_magtl_z = (((self.magtl_z3_raw << 16) | (self.magtl_z2_raw << 8)) | self.magtl_z1_raw)
            return self._m_magtl_z if hasattr(self, '_m_magtl_z') else None

        @property
        def antennas_status(self):
            """not set."""
            if hasattr(self, '_m_antennas_status'):
                return self._m_antennas_status if hasattr(self, '_m_antennas_status') else None

            self._m_antennas_status = (self.antennas_status_raw & 15)
            return self._m_antennas_status if hasattr(self, '_m_antennas_status') else None

        @property
        def gyro_x_mdps(self):
            """non zero if orientation enabled."""
            if hasattr(self, '_m_gyro_x_mdps'):
                return self._m_gyro_x_mdps if hasattr(self, '_m_gyro_x_mdps') else None

            self._m_gyro_x_mdps = (((self.gyro_x3_mdps_raw << 16) | (self.gyro_x2_mdps_raw << 8)) | self.gyro_x1_mdps_raw)
            return self._m_gyro_x_mdps if hasattr(self, '_m_gyro_x_mdps') else None

        @property
        def t_ab1(self):
            """not set."""
            if hasattr(self, '_m_t_ab1'):
                return self._m_t_ab1 if hasattr(self, '_m_t_ab1') else None

            self._m_t_ab1 = 0.0
            return self._m_t_ab1 if hasattr(self, '_m_t_ab1') else None

        @property
        def magtl_x(self):
            """non zero if orientation enabled."""
            if hasattr(self, '_m_magtl_x'):
                return self._m_magtl_x if hasattr(self, '_m_magtl_x') else None

            self._m_magtl_x = (((self.magtl_x3_raw << 16) | (self.magtl_x2_raw << 8)) | self.magtl_x1_raw)
            return self._m_magtl_x if hasattr(self, '_m_magtl_x') else None

        @property
        def gyro_y_mdps(self):
            """non zero if orientation enabled."""
            if hasattr(self, '_m_gyro_y_mdps'):
                return self._m_gyro_y_mdps if hasattr(self, '_m_gyro_y_mdps') else None

            self._m_gyro_y_mdps = (((self.gyro_y3_mdps_raw << 16) | (self.gyro_y2_mdps_raw << 8)) | self.gyro_y1_mdps_raw)
            return self._m_gyro_y_mdps if hasattr(self, '_m_gyro_y_mdps') else None

        @property
        def mode(self):
            if hasattr(self, '_m_mode'):
                return self._m_mode if hasattr(self, '_m_mode') else None

            self._m_mode = (u"Beacon" if self.sat_mode == 2 else (u"PostLauncheDepl" if self.sat_mode == 1 else (u"Recharge" if self.sat_mode == 3 else (u"Telecom" if self.sat_mode == 4 else (u"Failsafe" if self.sat_mode == 5 else (u"Off" if self.sat_mode == 6 else (u"Sun" if self.sat_mode == 7 else u"PostLaunche")))))))
            return self._m_mode if hasattr(self, '_m_mode') else None

        @property
        def gyro_z_mdps(self):
            if hasattr(self, '_m_gyro_z_mdps'):
                return self._m_gyro_z_mdps if hasattr(self, '_m_gyro_z_mdps') else None

            self._m_gyro_z_mdps = (((self.gyro_z3_mdps_raw << 16) | (self.gyro_z2_mdps_raw << 8)) | self.gyro_z1_mdps_raw)
            return self._m_gyro_z_mdps if hasattr(self, '_m_gyro_z_mdps') else None

        @property
        def t_ab2(self):
            """not set."""
            if hasattr(self, '_m_t_ab2'):
                return self._m_t_ab2 if hasattr(self, '_m_t_ab2') else None

            self._m_t_ab2 = (self.t_ab2_raw * 0.1)
            return self._m_t_ab2 if hasattr(self, '_m_t_ab2') else None

        @property
        def mux_i5_0(self):
            if hasattr(self, '_m_mux_i5_0'):
                return self._m_mux_i5_0 if hasattr(self, '_m_mux_i5_0') else None

            self._m_mux_i5_0 = (self.mux_i5_0_raw * 0.1)
            return self._m_mux_i5_0 if hasattr(self, '_m_mux_i5_0') else None


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class SsidMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ssid_mask = self._io.read_u1()

        @property
        def ssid(self):
            if hasattr(self, '_m_ssid'):
                return self._m_ssid if hasattr(self, '_m_ssid') else None

            self._m_ssid = ((self.ssid_mask & 15) >> 1)
            return self._m_ssid if hasattr(self, '_m_ssid') else None


    class Beacon2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.device_status = self._io.read_u2le()
            self.rtc_ss = self._io.read_s4le()
            self.temp2_raw = self._io.read_s2le()
            self.temp1_raw = self._io.read_s2le()
            self.u_3_3v_digi = self._io.read_s2le()
            self.u_3_3v_rf = self._io.read_s2le()
            self.u_3_3v_rf_amp = self._io.read_s2le()

        @property
        def temp2(self):
            """value [В°C]."""
            if hasattr(self, '_m_temp2'):
                return self._m_temp2 if hasattr(self, '_m_temp2') else None

            self._m_temp2 = (self.temp2_raw * 0.1)
            return self._m_temp2 if hasattr(self, '_m_temp2') else None

        @property
        def temp1(self):
            """value [В°C]."""
            if hasattr(self, '_m_temp1'):
                return self._m_temp1 if hasattr(self, '_m_temp1') else None

            self._m_temp1 = (self.temp1_raw * 0.1)
            return self._m_temp1 if hasattr(self, '_m_temp1') else None


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_type = self._io.read_u1()


    class Beacon0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.body = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")


    class CallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_callsign_ror = self._io.read_bytes(6)
            self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (1), 1)
            _io__raw_callsign_ror = KaitaiStream(BytesIO(self._raw_callsign_ror))
            self.callsign_ror = Polyitan1.Callsign(_io__raw_callsign_ror, self, self._root)


    class Ax25Info(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Polyitan1.Header(self._io, self, self._root)
            _on = self.header.data_type
            if _on == 0:
                self.data = Polyitan1.Beacon0(self._io, self, self._root)
            elif _on == 1:
                self.data = Polyitan1.Beacon1(self._io, self, self._root)
            elif _on == 2:
                self.data = Polyitan1.Beacon2(self._io, self, self._root)



