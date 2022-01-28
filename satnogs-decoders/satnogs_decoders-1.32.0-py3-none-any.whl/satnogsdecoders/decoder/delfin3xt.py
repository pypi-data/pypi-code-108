# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Delfin3xt(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field elapsed_time: ax25_frame.payload.ax25_payload.elapsed_time
    :field framecounter: ax25_frame.payload.ax25_payload.framecounter
    :field frametype: ax25_frame.payload.ax25_payload.frametype
    :field boot_counter: ax25_frame.payload.ax25_payload.boot_counter
    :field ptrx_dv: ax25_frame.payload.ax25_payload.ptrx_dv_raw
    :field ptrx_rss: ax25_frame.payload.ax25_payload.ptrx_rss_raw
    :field ptrx_rp: ax25_frame.payload.ax25_payload.ptrx_rp_raw
    :field ptrx_fp: ax25_frame.payload.ax25_payload.ptrx_fp_raw
    :field ptrx_tsc: ax25_frame.payload.ax25_payload.ptrx_tsc_raw
    :field ptrx_rsc: ax25_frame.payload.ax25_payload.ptrx_rsc_raw
    :field ptrx_pa_temp: ax25_frame.payload.ax25_payload.ptrx_pa_temp_raw
    :field ptrx_pbv: ax25_frame.payload.ax25_payload.ptrx_pbv_raw
    :field depl_sol_x_minus: ax25_frame.payload.ax25_payload.depl_sol_x_minus
    :field depl_sol_x_plus: ax25_frame.payload.ax25_payload.depl_sol_x_plus
    :field depl_sol_y_minus: ax25_frame.payload.ax25_payload.depl_sol_y_minus
    :field depl_sol_y_plus: ax25_frame.payload.ax25_payload.depl_sol_y_plus
    :field depl_ant_x_minus: ax25_frame.payload.ax25_payload.depl_ant_x_minus
    :field depl_ant_x_plus: ax25_frame.payload.ax25_payload.depl_ant_x_plus
    :field depl_ant_y_minus: ax25_frame.payload.ax25_payload.depl_ant_y_minus
    :field depl_ant_y_plus: ax25_frame.payload.ax25_payload.depl_ant_y_plus
    :field dab_temp: ax25_frame.payload.ax25_payload.dab_temp
    :field eps_bus_current: ax25_frame.payload.ax25_payload.eps_bus_current
    :field eps_bus_voltage: ax25_frame.payload.ax25_payload.eps_bus_voltage
    :field eps_variable_bus_v: ax25_frame.payload.ax25_payload.eps_variable_bus_v
    :field power_status_solar_panel_xpzp: ax25_frame.payload.ax25_payload.power_status_solar_panel_xpzp
    :field power_status_solar_panel_xpzm: ax25_frame.payload.ax25_payload.power_status_solar_panel_xpzm
    :field power_status_solar_panel_xmzp: ax25_frame.payload.ax25_payload.power_status_solar_panel_xmzp
    :field power_status_solar_panel_xmzm: ax25_frame.payload.ax25_payload.power_status_solar_panel_xmzm
    :field power_status_solar_panel_ypzp: ax25_frame.payload.ax25_payload.power_status_solar_panel_ypzp
    :field power_status_solar_panel_ypzm: ax25_frame.payload.ax25_payload.power_status_solar_panel_ypzm
    :field power_status_solar_panel_ymzp: ax25_frame.payload.ax25_payload.power_status_solar_panel_ymzp
    :field power_status_solar_panel_ymzm: ax25_frame.payload.ax25_payload.power_status_solar_panel_ymzm
    :field oppsp_xpzp_c: ax25_frame.payload.ax25_payload.oppsp_xpzp_c
    :field oppsp_xpzm_c: ax25_frame.payload.ax25_payload.oppsp_xpzm_c
    :field oppsp_xmzp_c: ax25_frame.payload.ax25_payload.oppsp_xmzp_c
    :field oppsp_xmzm_c: ax25_frame.payload.ax25_payload.oppsp_xmzm_c
    :field oppsp_ypzp_c: ax25_frame.payload.ax25_payload.oppsp_ypzp_c
    :field oppsp_ypzm_c: ax25_frame.payload.ax25_payload.oppsp_ypzm_c
    :field oppsp_ymzp_c: ax25_frame.payload.ax25_payload.oppsp_ymzp_c
    :field oppsp_ymzm_c: ax25_frame.payload.ax25_payload.oppsp_ymzm_c
    :field oppsp_xpzp_v: ax25_frame.payload.ax25_payload.oppsp_xpzp_v
    :field oppsp_xpzm_v: ax25_frame.payload.ax25_payload.oppsp_xpzm_v
    :field oppsp_xmzp_v: ax25_frame.payload.ax25_payload.oppsp_xmzp_v
    :field oppsp_xmzm_v: ax25_frame.payload.ax25_payload.oppsp_xmzm_v
    :field oppsp_ypzp_v: ax25_frame.payload.ax25_payload.oppsp_ypzp_v
    :field oppsp_ypzm_v: ax25_frame.payload.ax25_payload.oppsp_ypzm_v
    :field oppsp_ymzp_v: ax25_frame.payload.ax25_payload.oppsp_ymzp_v
    :field oppsp_ymzm_v: ax25_frame.payload.ax25_payload.oppsp_ymzm_v
    :field eps_solar_panel_xpzp_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_xpzp_temp
    :field eps_solar_panel_xpzm_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_xpzm_temp
    :field eps_solar_panel_xmzp_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_xmzp_temp
    :field eps_solar_panel_xmzm_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_xmzm_temp
    :field eps_solar_panel_ypzp_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_ypzp_temp
    :field eps_solar_panel_ypzm_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_ypzm_temp
    :field eps_solar_panel_ymzp_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_ymzp_temp
    :field eps_solar_panel_ymzm_temp: ax25_frame.payload.ax25_payload.eps_solar_panel_ymzm_temp
    :field eps_reg_board_temp: ax25_frame.payload.ax25_payload.eps_reg_board_temp
    :field bat1_dod: ax25_frame.payload.ax25_payload.bat1_dod
    :field bat1_cc: ax25_frame.payload.ax25_payload.bat1_cc
    :field bat1_dc: ax25_frame.payload.ax25_payload.bat1_dc
    :field bat1_v: ax25_frame.payload.ax25_payload.bat1_v
    :field bat1_temp: ax25_frame.payload.ax25_payload.bat1_temp
    :field bat2_dod: ax25_frame.payload.ax25_payload.bat2_dod
    :field bat2_cc: ax25_frame.payload.ax25_payload.bat2_cc
    :field bat2_dc: ax25_frame.payload.ax25_payload.bat2_dc
    :field bat2_v: ax25_frame.payload.ax25_payload.bat2_v
    :field bat2_temp: ax25_frame.payload.ax25_payload.bat2_temp
    :field bat3_dod: ax25_frame.payload.ax25_payload.bat3_dod
    :field bat3_cc: ax25_frame.payload.ax25_payload.bat3_cc
    :field bat3_dc: ax25_frame.payload.ax25_payload.bat3_dc
    :field bat3_v: ax25_frame.payload.ax25_payload.bat3_v
    :field bat3_temp: ax25_frame.payload.ax25_payload.bat3_temp
    :field bat4_dod: ax25_frame.payload.ax25_payload.bat4_dod
    :field bat4_cc: ax25_frame.payload.ax25_payload.bat4_cc
    :field bat4_dc: ax25_frame.payload.ax25_payload.bat4_dc
    :field bat4_v: ax25_frame.payload.ax25_payload.bat4_v
    :field bat4_temp: ax25_frame.payload.ax25_payload.bat4_temp
    :field t3_vc: ax25_frame.payload.ax25_payload.t3_vc
    :field t3_ic: ax25_frame.payload.ax25_payload.t3_ic
    :field t3_iv: ax25_frame.payload.ax25_payload.t3_iv
    :field t3_pt: ax25_frame.payload.ax25_payload.t3_pt
    :field t3_mt: ax25_frame.payload.ax25_payload.t3_mt
    :field t3_pp_1: ax25_frame.payload.ax25_payload.t3_pp_1
    :field t3_pp_2: ax25_frame.payload.ax25_payload.t3_pp_2
    :field t3_pp_3: ax25_frame.payload.ax25_payload.t3_pp_3
    :field t3_pp_4: ax25_frame.payload.ax25_payload.t3_pp_4
    :field t3_pp_5: ax25_frame.payload.ax25_payload.t3_pp_5
    :field t3_pp_6: ax25_frame.payload.ax25_payload.t3_pp_6
    :field t3_pp_7: ax25_frame.payload.ax25_payload.t3_pp_7
    :field t3_pp_8: ax25_frame.payload.ax25_payload.t3_pp_8
    :field t3_pp_9: ax25_frame.payload.ax25_payload.t3_pp_9
    :field t3_pp_10: ax25_frame.payload.ax25_payload.t3_pp_10
    :field t3_pp_11: ax25_frame.payload.ax25_payload.t3_pp_11
    :field t3_pp_12: ax25_frame.payload.ax25_payload.t3_pp_12
    :field t3_pp_13: ax25_frame.payload.ax25_payload.t3_pp_13
    :field t3_pp_14: ax25_frame.payload.ax25_payload.t3_pp_14
    :field t3_pp_15: ax25_frame.payload.ax25_payload.t3_pp_15
    :field t3_pp_16: ax25_frame.payload.ax25_payload.t3_pp_16
    :field t3_pp_17: ax25_frame.payload.ax25_payload.t3_pp_17
    :field t3_pp_18: ax25_frame.payload.ax25_payload.t3_pp_18
    :field t3_pp_19: ax25_frame.payload.ax25_payload.t3_pp_19
    :field t3_pp_20: ax25_frame.payload.ax25_payload.t3_pp_20
    :field t3_pp_21: ax25_frame.payload.ax25_payload.t3_pp_21
    :field t3_pp_22: ax25_frame.payload.ax25_payload.t3_pp_22
    :field t3_pp_23: ax25_frame.payload.ax25_payload.t3_pp_23
    :field t3_pp_24: ax25_frame.payload.ax25_payload.t3_pp_24
    :field t3_pp_25: ax25_frame.payload.ax25_payload.t3_pp_25
    :field t3_pp_26: ax25_frame.payload.ax25_payload.t3_pp_26
    :field t3_pp_27: ax25_frame.payload.ax25_payload.t3_pp_27
    :field t3_pp_28: ax25_frame.payload.ax25_payload.t3_pp_28
    :field t3_pp_29: ax25_frame.payload.ax25_payload.t3_pp_29
    :field t3_pp_30: ax25_frame.payload.ax25_payload.t3_pp_30
    :field t3_pp_31: ax25_frame.payload.ax25_payload.t3_pp_31
    :field t3_pp_32: ax25_frame.payload.ax25_payload.t3_pp_32
    :field t3_pp_33: ax25_frame.payload.ax25_payload.t3_pp_33
    :field t3_pp_34: ax25_frame.payload.ax25_payload.t3_pp_34
    :field t3_pp_35: ax25_frame.payload.ax25_payload.t3_pp_35
    :field t3_pp_36: ax25_frame.payload.ax25_payload.t3_pp_36
    :field t3_pp_37: ax25_frame.payload.ax25_payload.t3_pp_37
    :field t3_pp_38: ax25_frame.payload.ax25_payload.t3_pp_38
    :field t3_pp_39: ax25_frame.payload.ax25_payload.t3_pp_39
    :field t3_pp_40: ax25_frame.payload.ax25_payload.t3_pp_40
    :field t3_pp_41: ax25_frame.payload.ax25_payload.t3_pp_41
    :field t3_pp_42: ax25_frame.payload.ax25_payload.t3_pp_42
    :field t3_pp_43: ax25_frame.payload.ax25_payload.t3_pp_43
    :field t3_pp_44: ax25_frame.payload.ax25_payload.t3_pp_44
    :field t3_pp_45: ax25_frame.payload.ax25_payload.t3_pp_45
    :field t3_pp_46: ax25_frame.payload.ax25_payload.t3_pp_46
    :field t3_pp_47: ax25_frame.payload.ax25_payload.t3_pp_47
    :field t3_pp_48: ax25_frame.payload.ax25_payload.t3_pp_48
    :field t3_pp_49: ax25_frame.payload.ax25_payload.t3_pp_49
    :field t3_pp_50: ax25_frame.payload.ax25_payload.t3_pp_50
    :field t3_pp_51: ax25_frame.payload.ax25_payload.t3_pp_51
    :field t3_pp_52: ax25_frame.payload.ax25_payload.t3_pp_52
    :field t3_pp_53: ax25_frame.payload.ax25_payload.t3_pp_53
    :field t3_pp_54: ax25_frame.payload.ax25_payload.t3_pp_54
    :field t3_pp_55: ax25_frame.payload.ax25_payload.t3_pp_55
    :field t3_pp_56: ax25_frame.payload.ax25_payload.t3_pp_56
    :field t3_pp_57: ax25_frame.payload.ax25_payload.t3_pp_57
    :field t3_pp_58: ax25_frame.payload.ax25_payload.t3_pp_58
    :field t3_pp_59: ax25_frame.payload.ax25_payload.t3_pp_59
    :field t3_pp_60: ax25_frame.payload.ax25_payload.t3_pp_60
    :field sdm_iv_id: ax25_frame.payload.ax25_payload.sdm_iv_id
    :field skip: ax25_frame.payload.ax25_payload.skip
    :field sdm_status_cell_temp_ym: ax25_frame.payload.ax25_payload.sdm_status_cell_temp_ym
    :field sdm_status_cell_temp_yp: ax25_frame.payload.ax25_payload.sdm_status_cell_temp_yp
    :field sdm_iv_curve_c1: ax25_frame.payload.ax25_payload.sdm_iv_curve_c1
    :field sdm_iv_curve_c2: ax25_frame.payload.ax25_payload.sdm_iv_curve_c2
    :field sdm_iv_curve_c3: ax25_frame.payload.ax25_payload.sdm_iv_curve_c3
    :field sdm_iv_curve_c4: ax25_frame.payload.ax25_payload.sdm_iv_curve_c4
    :field sdm_iv_curve_c5: ax25_frame.payload.ax25_payload.sdm_iv_curve_c5
    :field sdm_iv_curve_c6: ax25_frame.payload.ax25_payload.sdm_iv_curve_c6
    :field sdm_iv_curve_c7: ax25_frame.payload.ax25_payload.sdm_iv_curve_c7
    :field sdm_iv_curve_c8: ax25_frame.payload.ax25_payload.sdm_iv_curve_c8
    :field sdm_iv_curve_v1: ax25_frame.payload.ax25_payload.sdm_iv_curve_v1
    :field sdm_iv_curve_v2: ax25_frame.payload.ax25_payload.sdm_iv_curve_v2
    :field sdm_iv_curve_v3: ax25_frame.payload.ax25_payload.sdm_iv_curve_v3
    :field sdm_iv_curve_v4: ax25_frame.payload.ax25_payload.sdm_iv_curve_v4
    :field sdm_iv_curve_v5: ax25_frame.payload.ax25_payload.sdm_iv_curve_v5
    :field sdm_iv_curve_v6: ax25_frame.payload.ax25_payload.sdm_iv_curve_v6
    :field sdm_iv_curve_v7: ax25_frame.payload.ax25_payload.sdm_iv_curve_v7
    :field sdm_iv_curve_v8: ax25_frame.payload.ax25_payload.sdm_iv_curve_v8
    :field sdm_cell_temp_ym: ax25_frame.payload.ax25_payload.sdm_cell_temp_ym
    :field sdm_cell_temp_yp: ax25_frame.payload.ax25_payload.sdm_cell_temp_yp
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Delfin3xt.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Delfin3xt.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Delfin3xt.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Delfin3xt.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Delfin3xt.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Delfin3xt.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Delfin3xt.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Delfin3xt.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Delfin3xt.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Delfin3xt.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Delfin3xt.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Delfin3xt.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_payload = self._io.read_bytes_full()
            _io__raw_ax25_payload = KaitaiStream(BytesIO(self._raw_ax25_payload))
            self.ax25_payload = Delfin3xt.Delfin3xtPayload(_io__raw_ax25_payload, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_payload = self._io.read_bytes_full()
            _io__raw_ax25_payload = KaitaiStream(BytesIO(self._raw_ax25_payload))
            self.ax25_payload = Delfin3xt.Delfin3xtPayload(_io__raw_ax25_payload, self, self._root)


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


    class Delfin3xtPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.elapsed_time = self._io.read_u4be()
            self.boot_counter = self._io.read_u2be()
            self.frame_ctr_type = self._io.read_u4be()
            self.ptrx_dv_raw = self._io.read_bits_int_be(12)
            self.ptrx_rss_raw = self._io.read_bits_int_be(12)
            self.ptrx_rp_raw = self._io.read_bits_int_be(12)
            self.ptrx_fp_raw = self._io.read_bits_int_be(12)
            self.ptrx_tsc_raw = self._io.read_bits_int_be(12)
            self.ptrx_rsc_raw = self._io.read_bits_int_be(12)
            self.ptrx_pa_temp_raw = self._io.read_bits_int_be(12)
            self.ptrx_pbv_raw = self._io.read_bits_int_be(12)
            self.depl_sol_x_minus = self._io.read_bits_int_be(1) != 0
            self.depl_sol_x_plus = self._io.read_bits_int_be(1) != 0
            self.depl_sol_y_minus = self._io.read_bits_int_be(1) != 0
            self.depl_sol_y_plus = self._io.read_bits_int_be(1) != 0
            self.depl_ant_x_minus = self._io.read_bits_int_be(1) != 0
            self.depl_ant_x_plus = self._io.read_bits_int_be(1) != 0
            self.depl_ant_y_minus = self._io.read_bits_int_be(1) != 0
            self.depl_ant_y_plus = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.dab_temp = self._io.read_u1()
            self.eps_bus_current = self._io.read_bits_int_be(12)
            self.eps_bus_voltage = self._io.read_bits_int_be(12)
            self._io.align_to_byte()
            self.eps_variable_bus_v = self._io.read_u1()
            self.power_status_solar_panel_xpzp = self._io.read_bits_int_be(1) != 0
            self.power_status_solar_panel_xpzm = self._io.read_bits_int_be(1) != 0
            self.power_status_solar_panel_xmzp = self._io.read_bits_int_be(1) != 0
            self.power_status_solar_panel_xmzm = self._io.read_bits_int_be(1) != 0
            self.power_status_solar_panel_ypzp = self._io.read_bits_int_be(1) != 0
            self.power_status_solar_panel_ypzm = self._io.read_bits_int_be(1) != 0
            self.power_status_solar_panel_ymzp = self._io.read_bits_int_be(1) != 0
            self.power_status_solar_panel_ymzm = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.oppsp_xpzp_c = self._io.read_u1()
            self.oppsp_xpzm_c = self._io.read_u1()
            self.oppsp_xmzp_c = self._io.read_u1()
            self.oppsp_xmzm_c = self._io.read_u1()
            self.oppsp_ypzp_c = self._io.read_u1()
            self.oppsp_ypzm_c = self._io.read_u1()
            self.oppsp_ymzp_c = self._io.read_u1()
            self.oppsp_ymzm_c = self._io.read_u1()
            self.oppsp_xpzp_v = self._io.read_u1()
            self.oppsp_xpzm_v = self._io.read_u1()
            self.oppsp_xmzp_v = self._io.read_u1()
            self.oppsp_xmzm_v = self._io.read_u1()
            self.oppsp_ypzp_v = self._io.read_u1()
            self.oppsp_ypzm_v = self._io.read_u1()
            self.oppsp_ymzp_v = self._io.read_u1()
            self.oppsp_ymzm_v = self._io.read_u1()
            self.eps_solar_panel_xpzp_temp = self._io.read_u1()
            self.eps_solar_panel_xpzm_temp = self._io.read_u1()
            self.eps_solar_panel_xmzp_temp = self._io.read_u1()
            self.eps_solar_panel_xmzm_temp = self._io.read_u1()
            self.eps_solar_panel_ypzp_temp = self._io.read_u1()
            self.eps_solar_panel_ypzm_temp = self._io.read_u1()
            self.eps_solar_panel_ymzp_temp = self._io.read_u1()
            self.eps_solar_panel_ymzm_temp = self._io.read_u1()
            self.eps_reg_board_temp = self._io.read_u1()
            self.bat1_dod = self._io.read_u1()
            self.bat1_cc = self._io.read_u1()
            self.bat1_dc = self._io.read_u1()
            self.bat1_v = self._io.read_u1()
            self.bat1_temp = self._io.read_u1()
            self.bat2_dod = self._io.read_u1()
            self.bat2_cc = self._io.read_u1()
            self.bat2_dc = self._io.read_u1()
            self.bat2_v = self._io.read_u1()
            self.bat2_temp = self._io.read_u1()
            self.bat3_dod = self._io.read_u1()
            self.bat3_cc = self._io.read_u1()
            self.bat3_dc = self._io.read_u1()
            self.bat3_v = self._io.read_u1()
            self.bat3_temp = self._io.read_u1()
            self.bat4_dod = self._io.read_u1()
            self.bat4_cc = self._io.read_u1()
            self.bat4_dc = self._io.read_u1()
            self.bat4_v = self._io.read_u1()
            self.bat4_temp = self._io.read_u1()
            self.t3_vc = self._io.read_u1()
            self.t3_ic = self._io.read_u1()
            self.t3_iv = self._io.read_u1()
            self.t3_pt = self._io.read_u1()
            self.t3_mt = self._io.read_u1()
            self.t3_pp_1 = self._io.read_bits_int_be(12)
            self.t3_pp_2 = self._io.read_bits_int_be(12)
            self.t3_pp_3 = self._io.read_bits_int_be(12)
            self.t3_pp_4 = self._io.read_bits_int_be(12)
            self.t3_pp_5 = self._io.read_bits_int_be(12)
            self.t3_pp_6 = self._io.read_bits_int_be(12)
            self.t3_pp_7 = self._io.read_bits_int_be(12)
            self.t3_pp_8 = self._io.read_bits_int_be(12)
            self.t3_pp_9 = self._io.read_bits_int_be(12)
            self.t3_pp_10 = self._io.read_bits_int_be(12)
            self.t3_pp_11 = self._io.read_bits_int_be(12)
            self.t3_pp_12 = self._io.read_bits_int_be(12)
            self.t3_pp_13 = self._io.read_bits_int_be(12)
            self.t3_pp_14 = self._io.read_bits_int_be(12)
            self.t3_pp_15 = self._io.read_bits_int_be(12)
            self.t3_pp_16 = self._io.read_bits_int_be(12)
            self.t3_pp_17 = self._io.read_bits_int_be(12)
            self.t3_pp_18 = self._io.read_bits_int_be(12)
            self.t3_pp_19 = self._io.read_bits_int_be(12)
            self.t3_pp_20 = self._io.read_bits_int_be(12)
            self.t3_pp_21 = self._io.read_bits_int_be(12)
            self.t3_pp_22 = self._io.read_bits_int_be(12)
            self.t3_pp_23 = self._io.read_bits_int_be(12)
            self.t3_pp_24 = self._io.read_bits_int_be(12)
            self.t3_pp_25 = self._io.read_bits_int_be(12)
            self.t3_pp_26 = self._io.read_bits_int_be(12)
            self.t3_pp_27 = self._io.read_bits_int_be(12)
            self.t3_pp_28 = self._io.read_bits_int_be(12)
            self.t3_pp_29 = self._io.read_bits_int_be(12)
            self.t3_pp_30 = self._io.read_bits_int_be(12)
            self.t3_pp_31 = self._io.read_bits_int_be(12)
            self.t3_pp_32 = self._io.read_bits_int_be(12)
            self.t3_pp_33 = self._io.read_bits_int_be(12)
            self.t3_pp_34 = self._io.read_bits_int_be(12)
            self.t3_pp_35 = self._io.read_bits_int_be(12)
            self.t3_pp_36 = self._io.read_bits_int_be(12)
            self.t3_pp_37 = self._io.read_bits_int_be(12)
            self.t3_pp_38 = self._io.read_bits_int_be(12)
            self.t3_pp_39 = self._io.read_bits_int_be(12)
            self.t3_pp_40 = self._io.read_bits_int_be(12)
            self.t3_pp_41 = self._io.read_bits_int_be(12)
            self.t3_pp_42 = self._io.read_bits_int_be(12)
            self.t3_pp_43 = self._io.read_bits_int_be(12)
            self.t3_pp_44 = self._io.read_bits_int_be(12)
            self.t3_pp_45 = self._io.read_bits_int_be(12)
            self.t3_pp_46 = self._io.read_bits_int_be(12)
            self.t3_pp_47 = self._io.read_bits_int_be(12)
            self.t3_pp_48 = self._io.read_bits_int_be(12)
            self.t3_pp_49 = self._io.read_bits_int_be(12)
            self.t3_pp_50 = self._io.read_bits_int_be(12)
            self.t3_pp_51 = self._io.read_bits_int_be(12)
            self.t3_pp_52 = self._io.read_bits_int_be(12)
            self.t3_pp_53 = self._io.read_bits_int_be(12)
            self.t3_pp_54 = self._io.read_bits_int_be(12)
            self.t3_pp_55 = self._io.read_bits_int_be(12)
            self.t3_pp_56 = self._io.read_bits_int_be(12)
            self.t3_pp_57 = self._io.read_bits_int_be(12)
            self.t3_pp_58 = self._io.read_bits_int_be(12)
            self.t3_pp_59 = self._io.read_bits_int_be(12)
            self.t3_pp_60 = self._io.read_bits_int_be(12)
            self.sdm_iv_id = self._io.read_bits_int_be(4)
            self.skip = self._io.read_bits_int_be(2)
            self.sdm_status_cell_temp_ym = self._io.read_bits_int_be(1) != 0
            self.sdm_status_cell_temp_yp = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.sdm_iv_curve_c1 = self._io.read_u2be()
            self.sdm_iv_curve_c2 = self._io.read_u2be()
            self.sdm_iv_curve_c3 = self._io.read_u2be()
            self.sdm_iv_curve_c4 = self._io.read_u2be()
            self.sdm_iv_curve_c5 = self._io.read_u2be()
            self.sdm_iv_curve_c6 = self._io.read_u2be()
            self.sdm_iv_curve_c7 = self._io.read_u2be()
            self.sdm_iv_curve_c8 = self._io.read_u2be()
            self.sdm_iv_curve_v1 = self._io.read_u2be()
            self.sdm_iv_curve_v2 = self._io.read_u2be()
            self.sdm_iv_curve_v3 = self._io.read_u2be()
            self.sdm_iv_curve_v4 = self._io.read_u2be()
            self.sdm_iv_curve_v5 = self._io.read_u2be()
            self.sdm_iv_curve_v6 = self._io.read_u2be()
            self.sdm_iv_curve_v7 = self._io.read_u2be()
            self.sdm_iv_curve_v8 = self._io.read_u2be()
            self.sdm_cell_temp_ym = self._io.read_u1()
            self.sdm_cell_temp_yp = self._io.read_u1()

        @property
        def payloadsize(self):
            if hasattr(self, '_m_payloadsize'):
                return self._m_payloadsize if hasattr(self, '_m_payloadsize') else None

            self._m_payloadsize = self._io.size()
            return self._m_payloadsize if hasattr(self, '_m_payloadsize') else None

        @property
        def framecounter(self):
            if hasattr(self, '_m_framecounter'):
                return self._m_framecounter if hasattr(self, '_m_framecounter') else None

            self._m_framecounter = ((self.frame_ctr_type & 4294967294) >> 1)
            return self._m_framecounter if hasattr(self, '_m_framecounter') else None

        @property
        def frametype(self):
            if hasattr(self, '_m_frametype'):
                return self._m_frametype if hasattr(self, '_m_frametype') else None

            self._m_frametype = (self.frame_ctr_type & 1)
            return self._m_frametype if hasattr(self, '_m_frametype') else None


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
            self.callsign_ror = Delfin3xt.Callsign(_io__raw_callsign_ror, self, self._root)



