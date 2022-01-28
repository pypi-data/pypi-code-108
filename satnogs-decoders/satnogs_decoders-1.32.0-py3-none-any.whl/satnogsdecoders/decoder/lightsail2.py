# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Lightsail2(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field src_ip_addr: ax25_frame.payload.ax25_info.src_ip_addr
    :field dst_ip_addr: ax25_frame.payload.ax25_info.dst_ip_addr
    :field src_port: ax25_frame.payload.ax25_info.body.src_port
    :field dst_port: ax25_frame.payload.ax25_info.body.dst_port
    :field type: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.type
    :field daughter_atmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.daughter_atmp
    :field daughter_btmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.daughter_btmp
    :field threev_pltmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.threev_pltmp
    :field rf_amptmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.rf_amptmp
    :field nx_tmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nx_tmp
    :field px_tmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.px_tmp
    :field ny_tmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.ny_tmp
    :field py_tmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.py_tmp
    :field nz_tmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nz_tmp
    :field pz_tmp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.pz_tmp
    :field atmelpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.atmelpwrcurr
    :field atmelpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.atmelpwrbusv
    :field threev_pwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.threev_pwrcurr
    :field threev_pwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.threev_pwrbusv
    :field threev_plpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.threev_plpwrcurr
    :field threev_plpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.threev_plpwrbusv
    :field fivev_plpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.fivev_plpwrcurr
    :field fivev_plpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.fivev_plpwrbusv
    :field daughter_apwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.daughter_apwrcurr
    :field daughter_apwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.daughter_apwrbusv
    :field daughter_bpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.daughter_bpwrcurr
    :field daughter_bpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.daughter_bpwrbusv
    :field nx_intpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nx_intpwrcurr
    :field nx_intpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nx_intpwrbusv
    :field nx_extpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nx_extpwrcurr
    :field nx_extpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nx_extpwrbusv
    :field px_intpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.px_intpwrcurr
    :field px_intpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.px_intpwrbusv
    :field px_extpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.px_extpwrcurr
    :field px_extpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.px_extpwrbusv
    :field ny_intpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.ny_intpwrcurr
    :field ny_intpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.ny_intpwrbusv
    :field ny_extpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.ny_extpwrcurr
    :field ny_extpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.ny_extpwrbusv
    :field py_intpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.py_intpwrcurr
    :field py_intpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.py_intpwrbusv
    :field py_extpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.py_extpwrcurr
    :field py_extpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.py_extpwrbusv
    :field nz_extpwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nz_extpwrcurr
    :field nz_extpwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nz_extpwrbusv
    :field usercputime: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.usercputime
    :field syscputime: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.syscputime
    :field idlecputime: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.idlecputime
    :field processes: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.processes
    :field memfree: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.memfree
    :field buffers: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.buffers
    :field cached: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.cached
    :field datafree: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.datafree
    :field nanderasures: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.nanderasures
    :field beaconcnt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.beaconcnt
    :field time: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.time
    :field boottime: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.boottime
    :field long_dur_counter: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sys.long_dur_counter
    :field batt_pwr_draw: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.battPwrDraw
    :field adcs_mode: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.adcs_mode
    :field flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.flags
    :field q0_act: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.q0_act
    :field q1_act: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.q1_act
    :field q2_act: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.q2_act
    :field q3_act: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.q3_act
    :field x_rate: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.x_rate
    :field y_rate: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.y_rate
    :field z_rate: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.z_rate
    :field gyro_px: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.gyro_pxy.val_a
    :field gyro_py: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.gyro_pxy.val_b
    :field gyro_iz: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.gyro_piz.val_a
    :field gyro_pz: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.gyro_piz.val_b
    :field gyro_ix: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.gyro_ixy.val_a
    :field gyro_iy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.gyro_ixy.val_b
    :field sol_nxx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_nxx
    :field sol_nxy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_nxy
    :field sol_nyx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_nyx
    :field sol_nyy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_nyy
    :field sol_nzx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_nzx
    :field sol_nzy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_nzy
    :field sol_pxx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_pxx
    :field sol_pxy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_pxy
    :field sol_pyx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_pyx
    :field sol_pyy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.sol_pyy
    :field mag_nxx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_nxxy.val_a
    :field mag_nxy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_nxxy.val_b
    :field mag_nxz: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_npxz.val_a
    :field mag_pxz: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_npxz.val_b
    :field mag_pxx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_pxxy.val_a
    :field mag_pxy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_pxxy.val_b
    :field mag_nyz: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_npyz.val_a
    :field mag_pyz: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_npyz.val_b
    :field mag_pyx: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_pyxy.val_a
    :field mag_pyy: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.mag_pyxy.val_b
    :field wheel_rpm: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.wheel_rpm
    :field cam0_status: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam0.status
    :field cam0_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam0.temp
    :field cam0_last_contact: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam0.last_contact
    :field cam0_pics_remaining: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam0.pics_remaining
    :field cam0_retry_fails: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam0.retry_fails
    :field cam1_status: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam1.status
    :field cam1_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam1.temp
    :field cam1_last_contact: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam1.last_contact
    :field cam1_pics_remaining: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam1.pics_remaining
    :field cam1_retry_fails: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.cam1.retry_fails
    :field torqx_pwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.torqx_pwrcurr
    :field torqx_pwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.torqx_pwrbusv
    :field torqy_pwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.torqy_pwrcurr
    :field torqy_pwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.torqy_pwrbusv
    :field torqz_pwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.torqz_pwrcurr
    :field torqz_pwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.torqz_pwrbusv
    :field motor_pwrcurr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.motor_pwrcurr
    :field motor_pwrbusv: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.motor_pwrbusv
    :field pic_panel_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.pic_panel_flags
    :field motor_cnt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.motor_cnt
    :field motor_limit: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.motor_limit
    :field bat0_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat0.curr
    :field bat0_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat0.volt
    :field bat0_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat0.temp
    :field bat0_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat0.flags
    :field bat0_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat0.ctlflags
    :field bat1_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat1.curr
    :field bat1_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat1.volt
    :field bat1_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat1.temp
    :field bat1_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat1.flags
    :field bat1_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat1.ctlflags
    :field bat2_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat2.curr
    :field bat2_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat2.volt
    :field bat2_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat2.temp
    :field bat2_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat2.flags
    :field bat2_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat2.ctlflags
    :field bat3_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat3.curr
    :field bat3_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat3.volt
    :field bat3_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat3.temp
    :field bat3_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat3.flags
    :field bat3_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat3.ctlflags
    :field bat4_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat4.curr
    :field bat4_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat4.volt
    :field bat4_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat4.temp
    :field bat4_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat4.flags
    :field bat4_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat4.ctlflags
    :field bat5_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat5.curr
    :field bat5_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat5.volt
    :field bat5_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat5.temp
    :field bat5_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat5.flags
    :field bat5_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat5.ctlflags
    :field bat6_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat6.curr
    :field bat6_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat6.volt
    :field bat6_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat6.temp
    :field bat6_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat6.flags
    :field bat6_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat6.ctlflags
    :field bat7_curr: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat7.curr
    :field bat7_volt: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat7.volt
    :field bat7_temp: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat7.temp
    :field bat7_flags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat7.flags
    :field bat7_ctlflags: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.bat7.ctlflags
    :field comm_rxcount: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.comm.rxcount
    :field comm_txcount: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.comm.txcount
    :field comm_rxbytes: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.comm.rxbytes
    :field comm_txbytes: ax25_frame.payload.ax25_info.body.body.lsb_beacondata.comm.txbytes
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Lightsail2.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Lightsail2.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Lightsail2.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Lightsail2.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Lightsail2.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Lightsail2.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Lightsail2.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Lightsail2.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Lightsail2.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Lightsail2.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Lightsail2.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Lightsail2.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self.pid
            if _on == 204:
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Lightsail2.Ipv4Pkt(_io__raw_ax25_info, self, self._root)
            elif _on == 240:
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Lightsail2.NoneL3(_io__raw_ax25_info, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ascii")


    class LsbBatterydataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.curr = self._io.read_s1()
            self.volt = self._io.read_u1()
            self.temp = self._io.read_u1()
            self.flags = self._io.read_u1()
            self.ctlflags = self._io.read_u1()


    class Packedsigned2x12T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a_high = self._io.read_s1()
            self.b_high = self._io.read_s1()
            self.ab_low = self._io.read_u1()

        @property
        def val_a(self):
            if hasattr(self, '_m_val_a'):
                return self._m_val_a if hasattr(self, '_m_val_a') else None

            self._m_val_a = ((self.a_high << 4) | (self.ab_low & 15))
            return self._m_val_a if hasattr(self, '_m_val_a') else None

        @property
        def val_b(self):
            if hasattr(self, '_m_val_b'):
                return self._m_val_b if hasattr(self, '_m_val_b') else None

            self._m_val_b = ((self.b_high << 4) | (self.ab_low & (240 >> 4)))
            return self._m_val_b if hasattr(self, '_m_val_b') else None


    class UdpPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lsb_beacondata = Lightsail2.LsbBeacondataT(self._io, self, self._root)


    class Ipv4Options(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while not self._io.is_eof():
                self.entries.append(Lightsail2.Ipv4Option(self._io, self, self._root))
                i += 1



    class NoNextHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass


    class Ipv6Pkt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_bits_int_be(4)
            self.traffic_class = self._io.read_bits_int_be(8)
            self.flow_label = self._io.read_bits_int_be(20)
            self._io.align_to_byte()
            self.payload_length = self._io.read_u2be()
            self.next_header_type = self._io.read_u1()
            self.hop_limit = self._io.read_u1()
            self.src_ipv6_addr = self._io.read_bytes(16)
            self.dst_ipv6_addr = self._io.read_bytes(16)
            _on = self.next_header_type
            if _on == 17:
                self.next_header = Lightsail2.UdpDtgrm(self._io, self, self._root)
            elif _on == 0:
                self.next_header = Lightsail2.OptionHopByHop(self._io, self, self._root)
            elif _on == 4:
                self.next_header = Lightsail2.Ipv4Pkt(self._io, self, self._root)
            elif _on == 6:
                self.next_header = Lightsail2.TcpSegm(self._io, self, self._root)
            elif _on == 59:
                self.next_header = Lightsail2.NoNextHeader(self._io, self, self._root)
            self.rest = self._io.read_bytes_full()


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


    class CamerainfoT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status = self._io.read_u1()
            self.temp = self._io.read_u1()
            self.last_contact = self._io.read_u1()
            self.pics_remaining = self._io.read_bits_int_be(6)
            self.retry_fails = self._io.read_bits_int_be(2)


    class LsbSysmgrdataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_u1()
            self.daughter_atmp = self._io.read_u1()
            self.daughter_btmp = self._io.read_u1()
            self.threev_pltmp = self._io.read_u1()
            self.rf_amptmp = self._io.read_u1()
            self.nx_tmp = self._io.read_u1()
            self.px_tmp = self._io.read_u1()
            self.ny_tmp = self._io.read_u1()
            self.py_tmp = self._io.read_u1()
            self.nz_tmp = self._io.read_u1()
            self.pz_tmp = self._io.read_u1()
            self.atmelpwrcurr = self._io.read_u1()
            self.atmelpwrbusv = self._io.read_u1()
            self.threev_pwrcurr = self._io.read_u1()
            self.threev_pwrbusv = self._io.read_u1()
            self.threev_plpwrcurr = self._io.read_u1()
            self.threev_plpwrbusv = self._io.read_u1()
            self.fivev_plpwrcurr = self._io.read_u1()
            self.fivev_plpwrbusv = self._io.read_u1()
            self.daughter_apwrcurr = self._io.read_u1()
            self.daughter_apwrbusv = self._io.read_u1()
            self.daughter_bpwrcurr = self._io.read_u1()
            self.daughter_bpwrbusv = self._io.read_u1()
            self.nx_intpwrcurr = self._io.read_u1()
            self.nx_intpwrbusv = self._io.read_u1()
            self.nx_extpwrcurr = self._io.read_u1()
            self.nx_extpwrbusv = self._io.read_u1()
            self.px_intpwrcurr = self._io.read_u1()
            self.px_intpwrbusv = self._io.read_u1()
            self.px_extpwrcurr = self._io.read_u1()
            self.px_extpwrbusv = self._io.read_u1()
            self.ny_intpwrcurr = self._io.read_u1()
            self.ny_intpwrbusv = self._io.read_u1()
            self.ny_extpwrcurr = self._io.read_u1()
            self.ny_extpwrbusv = self._io.read_u1()
            self.py_intpwrcurr = self._io.read_u1()
            self.py_intpwrbusv = self._io.read_u1()
            self.py_extpwrcurr = self._io.read_u1()
            self.py_extpwrbusv = self._io.read_u1()
            self.nz_extpwrcurr = self._io.read_u1()
            self.nz_extpwrbusv = self._io.read_u1()
            self.usercputime = self._io.read_u4be()
            self.syscputime = self._io.read_u4be()
            self.idlecputime = self._io.read_u4be()
            self.processes = self._io.read_u4be()
            self.memfree = self._io.read_u4be()
            self.buffers = self._io.read_u4be()
            self.cached = self._io.read_u4be()
            self.datafree = self._io.read_u4be()
            self.nanderasures = self._io.read_u4be()
            self.beaconcnt = self._io.read_u2be()
            self.time = self._io.read_u4be()
            self.boottime = self._io.read_u4be()
            self.long_dur_counter = self._io.read_u2be()


    class Ipv4Pkt(KaitaiStruct):

        class ProtocolEnum(Enum):
            hopopt = 0
            icmp = 1
            igmp = 2
            ggp = 3
            ipv4 = 4
            st = 5
            tcp = 6
            cbt = 7
            egp = 8
            igp = 9
            bbn_rcc_mon = 10
            nvp_ii = 11
            pup = 12
            argus = 13
            emcon = 14
            xnet = 15
            chaos = 16
            udp = 17
            mux = 18
            dcn_meas = 19
            hmp = 20
            prm = 21
            xns_idp = 22
            trunk_1 = 23
            trunk_2 = 24
            leaf_1 = 25
            leaf_2 = 26
            rdp = 27
            irtp = 28
            iso_tp4 = 29
            netblt = 30
            mfe_nsp = 31
            merit_inp = 32
            dccp = 33
            x_3pc = 34
            idpr = 35
            xtp = 36
            ddp = 37
            idpr_cmtp = 38
            tp_plus_plus = 39
            il = 40
            ipv6 = 41
            sdrp = 42
            ipv6_route = 43
            ipv6_frag = 44
            idrp = 45
            rsvp = 46
            gre = 47
            dsr = 48
            bna = 49
            esp = 50
            ah = 51
            i_nlsp = 52
            swipe = 53
            narp = 54
            mobile = 55
            tlsp = 56
            skip = 57
            ipv6_icmp = 58
            ipv6_nonxt = 59
            ipv6_opts = 60
            any_host_internal_protocol = 61
            cftp = 62
            any_local_network = 63
            sat_expak = 64
            kryptolan = 65
            rvd = 66
            ippc = 67
            any_distributed_file_system = 68
            sat_mon = 69
            visa = 70
            ipcv = 71
            cpnx = 72
            cphb = 73
            wsn = 74
            pvp = 75
            br_sat_mon = 76
            sun_nd = 77
            wb_mon = 78
            wb_expak = 79
            iso_ip = 80
            vmtp = 81
            secure_vmtp = 82
            vines = 83
            ttp = 84
            nsfnet_igp = 85
            dgp = 86
            tcf = 87
            eigrp = 88
            ospfigp = 89
            sprite_rpc = 90
            larp = 91
            mtp = 92
            ax_25 = 93
            ipip = 94
            micp = 95
            scc_sp = 96
            etherip = 97
            encap = 98
            any_private_encryption_scheme = 99
            gmtp = 100
            ifmp = 101
            pnni = 102
            pim = 103
            aris = 104
            scps = 105
            qnx = 106
            a_n = 107
            ipcomp = 108
            snp = 109
            compaq_peer = 110
            ipx_in_ip = 111
            vrrp = 112
            pgm = 113
            any_0_hop = 114
            l2tp = 115
            ddx = 116
            iatp = 117
            stp = 118
            srp = 119
            uti = 120
            smp = 121
            sm = 122
            ptp = 123
            isis_over_ipv4 = 124
            fire = 125
            crtp = 126
            crudp = 127
            sscopmce = 128
            iplt = 129
            sps = 130
            pipe = 131
            sctp = 132
            fc = 133
            rsvp_e2e_ignore = 134
            mobility_header = 135
            udplite = 136
            mpls_in_ip = 137
            manet = 138
            hip = 139
            shim6 = 140
            wesp = 141
            rohc = 142
            reserved_255 = 255
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b1 = self._io.read_u1()
            self.b2 = self._io.read_u1()
            self.total_length = self._io.read_u2be()
            self.identification = self._io.read_u2be()
            self.b67 = self._io.read_u2be()
            self.ttl = self._io.read_u1()
            self.protocol = KaitaiStream.resolve_enum(Lightsail2.Ipv4Pkt.ProtocolEnum, self._io.read_u1())
            self.header_checksum = self._io.read_u2be()
            self.src_ip_addr = self._io.read_u4be()
            self.dst_ip_addr = self._io.read_u4be()
            self._raw_options = self._io.read_bytes((self.ihl_bytes - 20))
            _io__raw_options = KaitaiStream(BytesIO(self._raw_options))
            self.options = Lightsail2.Ipv4Options(_io__raw_options, self, self._root)
            _on = self.protocol
            if _on == Lightsail2.Ipv4Pkt.ProtocolEnum.udp:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = Lightsail2.UdpDtgrm(_io__raw_body, self, self._root)
            elif _on == Lightsail2.Ipv4Pkt.ProtocolEnum.icmp:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = Lightsail2.IcmpPkt(_io__raw_body, self, self._root)
            elif _on == Lightsail2.Ipv4Pkt.ProtocolEnum.ipv6:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = Lightsail2.Ipv6Pkt(_io__raw_body, self, self._root)
            elif _on == Lightsail2.Ipv4Pkt.ProtocolEnum.tcp:
                self._raw_body = self._io.read_bytes((self.total_length - self.ihl_bytes))
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = Lightsail2.TcpSegm(_io__raw_body, self, self._root)
            else:
                self.body = self._io.read_bytes((self.total_length - self.ihl_bytes))

        @property
        def version(self):
            if hasattr(self, '_m_version'):
                return self._m_version if hasattr(self, '_m_version') else None

            self._m_version = ((self.b1 & 240) >> 4)
            return self._m_version if hasattr(self, '_m_version') else None

        @property
        def ihl(self):
            if hasattr(self, '_m_ihl'):
                return self._m_ihl if hasattr(self, '_m_ihl') else None

            self._m_ihl = (self.b1 & 15)
            return self._m_ihl if hasattr(self, '_m_ihl') else None

        @property
        def ihl_bytes(self):
            if hasattr(self, '_m_ihl_bytes'):
                return self._m_ihl_bytes if hasattr(self, '_m_ihl_bytes') else None

            self._m_ihl_bytes = (self.ihl * 4)
            return self._m_ihl_bytes if hasattr(self, '_m_ihl_bytes') else None


    class TcpSegm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.src_port = self._io.read_u2be()
            self.dst_port = self._io.read_u2be()
            self.seq_num = self._io.read_u4be()
            self.ack_num = self._io.read_u4be()
            self.b12 = self._io.read_u1()
            self.b13 = self._io.read_u1()
            self.window_size = self._io.read_u2be()
            self.checksum = self._io.read_u2be()
            self.urgent_pointer = self._io.read_u2be()
            self.body = self._io.read_bytes_full()


    class NoneL3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes_full()


    class LsbBeacondataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sys = Lightsail2.LsbSysmgrdataT(self._io, self, self._root)
            self.comm = Lightsail2.LsbCommdataT(self._io, self, self._root)
            self.bat0 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.bat1 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.bat2 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.bat3 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.bat4 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.bat5 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.bat6 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.bat7 = Lightsail2.LsbBatterydataT(self._io, self, self._root)
            self.batt_pwr_draw = self._io.read_s2be()
            self.adcs_mode = self._io.read_u1()
            self.flags = self._io.read_u1()
            self.q0_act = self._io.read_s2be()
            self.q1_act = self._io.read_s2be()
            self.q2_act = self._io.read_s2be()
            self.q3_act = self._io.read_s2be()
            self.x_rate = self._io.read_s2be()
            self.y_rate = self._io.read_s2be()
            self.z_rate = self._io.read_s2be()
            self.gyro_pxy = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.gyro_piz = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.gyro_ixy = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.sol_nxx = self._io.read_u2be()
            self.sol_nxy = self._io.read_u2be()
            self.sol_nyx = self._io.read_u2be()
            self.sol_nyy = self._io.read_u2be()
            self.sol_nzx = self._io.read_u2be()
            self.sol_nzy = self._io.read_u2be()
            self.sol_pxx = self._io.read_u2be()
            self.sol_pxy = self._io.read_u2be()
            self.sol_pyx = self._io.read_u2be()
            self.sol_pyy = self._io.read_u2be()
            self.mag_nxxy = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.mag_npxz = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.mag_pxxy = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.mag_npyz = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.mag_pyxy = Lightsail2.Packedsigned2x12T(self._io, self, self._root)
            self.wheel_rpm = self._io.read_s2be()
            self.cam0 = Lightsail2.CamerainfoT(self._io, self, self._root)
            self.cam1 = Lightsail2.CamerainfoT(self._io, self, self._root)
            self.torqx_pwrcurr = self._io.read_u1()
            self.torqx_pwrbusv = self._io.read_s1()
            self.torqy_pwrcurr = self._io.read_u1()
            self.torqy_pwrbusv = self._io.read_s1()
            self.torqz_pwrcurr = self._io.read_u1()
            self.torqz_pwrbusv = self._io.read_s1()
            self.motor_pwrcurr = self._io.read_u1()
            self.motor_pwrbusv = self._io.read_u1()
            self.pic_panel_flags = self._io.read_u1()
            self.motor_cnt_high = self._io.read_s1()
            self.motor_cnt_low = self._io.read_u2be()
            self.motor_limit_high = self._io.read_s1()
            self.motor_limit_low = self._io.read_u2be()

        @property
        def motor_cnt(self):
            if hasattr(self, '_m_motor_cnt'):
                return self._m_motor_cnt if hasattr(self, '_m_motor_cnt') else None

            self._m_motor_cnt = ((self.motor_cnt_high << 16) | self.motor_cnt_low)
            return self._m_motor_cnt if hasattr(self, '_m_motor_cnt') else None

        @property
        def motor_limit(self):
            if hasattr(self, '_m_motor_limit'):
                return self._m_motor_limit if hasattr(self, '_m_motor_limit') else None

            self._m_motor_limit = ((self.motor_limit_high << 16) | self.motor_limit_low)
            return self._m_motor_limit if hasattr(self, '_m_motor_limit') else None


    class UdpDtgrm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.src_port = self._io.read_u2be()
            self.dst_port = self._io.read_u2be()
            self.length = self._io.read_u2be()
            self.checksum = self._io.read_u2be()
            self._raw_body = self._io.read_bytes_full()
            _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
            self.body = Lightsail2.UdpPayload(_io__raw_body, self, self._root)


    class Packedunsigned2x12T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a_high = self._io.read_u1()
            self.b_high = self._io.read_u1()
            self.ab_low = self._io.read_u1()

        @property
        def val_a(self):
            if hasattr(self, '_m_val_a'):
                return self._m_val_a if hasattr(self, '_m_val_a') else None

            self._m_val_a = ((self.a_high << 4) | (self.ab_low & 15))
            return self._m_val_a if hasattr(self, '_m_val_a') else None

        @property
        def val_b(self):
            if hasattr(self, '_m_val_b'):
                return self._m_val_b if hasattr(self, '_m_val_b') else None

            self._m_val_b = ((self.b_high << 4) | (self.ab_low & (240 >> 4)))
            return self._m_val_b if hasattr(self, '_m_val_b') else None


    class DestinationUnreachableMsg(KaitaiStruct):

        class DestinationUnreachableCode(Enum):
            net_unreachable = 0
            host_unreachable = 1
            protocol_unreachable = 2
            port_unreachable = 3
            fragmentation_needed_and_df_set = 4
            source_route_failed = 5
            dst_net_unkown = 6
            sdt_host_unkown = 7
            src_isolated = 8
            net_prohibited_by_admin = 9
            host_prohibited_by_admin = 10
            net_unreachable_for_tos = 11
            host_unreachable_for_tos = 12
            communication_prohibited_by_admin = 13
            host_precedence_violation = 14
            precedence_cuttoff_in_effect = 15
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = KaitaiStream.resolve_enum(Lightsail2.DestinationUnreachableMsg.DestinationUnreachableCode, self._io.read_u1())
            self.checksum = self._io.read_u2be()


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
            self.callsign_ror = Lightsail2.Callsign(_io__raw_callsign_ror, self, self._root)


    class LsbCommdataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rxcount = self._io.read_u2be()
            self.txcount = self._io.read_u2be()
            self.rxbytes = self._io.read_u4be()
            self.txbytes = self._io.read_u4be()


    class OptionHopByHop(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.next_header_type = self._io.read_u1()
            self.hdr_ext_len = self._io.read_u1()
            self.body = self._io.read_bytes((self.hdr_ext_len - 1))
            _on = self.next_header_type
            if _on == 0:
                self.next_header = Lightsail2.OptionHopByHop(self._io, self, self._root)
            elif _on == 6:
                self.next_header = Lightsail2.TcpSegm(self._io, self, self._root)
            elif _on == 59:
                self.next_header = Lightsail2.NoNextHeader(self._io, self, self._root)


    class EchoMsg(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = self._io.read_bytes(1)
            if not self.code == b"\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.code, self._io, u"/types/echo_msg/seq/0")
            self.checksum = self._io.read_u2be()
            self.identifier = self._io.read_u2be()
            self.seq_num = self._io.read_u2be()
            self.data = self._io.read_bytes_full()


    class TimeExceededMsg(KaitaiStruct):

        class TimeExceededCode(Enum):
            time_to_live_exceeded_in_transit = 0
            fragment_reassembly_time_exceeded = 1
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = KaitaiStream.resolve_enum(Lightsail2.TimeExceededMsg.TimeExceededCode, self._io.read_u1())
            self.checksum = self._io.read_u2be()


    class IcmpPkt(KaitaiStruct):

        class IcmpTypeEnum(Enum):
            echo_reply = 0
            destination_unreachable = 3
            source_quench = 4
            redirect = 5
            echo = 8
            time_exceeded = 11
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.icmp_type = KaitaiStream.resolve_enum(Lightsail2.IcmpPkt.IcmpTypeEnum, self._io.read_u1())
            if self.icmp_type == Lightsail2.IcmpPkt.IcmpTypeEnum.destination_unreachable:
                self.destination_unreachable = Lightsail2.DestinationUnreachableMsg(self._io, self, self._root)

            if self.icmp_type == Lightsail2.IcmpPkt.IcmpTypeEnum.time_exceeded:
                self.time_exceeded = Lightsail2.TimeExceededMsg(self._io, self, self._root)

            if  ((self.icmp_type == Lightsail2.IcmpPkt.IcmpTypeEnum.echo) or (self.icmp_type == Lightsail2.IcmpPkt.IcmpTypeEnum.echo_reply)) :
                self.echo = Lightsail2.EchoMsg(self._io, self, self._root)



    class Ipv4Option(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.b1 = self._io.read_u1()
            self.len = self._io.read_u1()
            self.body = self._io.read_bytes(((self.len - 2) if self.len > 2 else 0))

        @property
        def copy(self):
            if hasattr(self, '_m_copy'):
                return self._m_copy if hasattr(self, '_m_copy') else None

            self._m_copy = ((self.b1 & 128) >> 7)
            return self._m_copy if hasattr(self, '_m_copy') else None

        @property
        def opt_class(self):
            if hasattr(self, '_m_opt_class'):
                return self._m_opt_class if hasattr(self, '_m_opt_class') else None

            self._m_opt_class = ((self.b1 & 96) >> 5)
            return self._m_opt_class if hasattr(self, '_m_opt_class') else None

        @property
        def number(self):
            if hasattr(self, '_m_number'):
                return self._m_number if hasattr(self, '_m_number') else None

            self._m_number = (self.b1 & 31)
            return self._m_number if hasattr(self, '_m_number') else None



