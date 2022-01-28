# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Duchifat3(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field service_type: ax25_frame.payload.ax25_info.service_type
    :field sub_service_type: ax25_frame.payload.ax25_info.sub_service_type
    :field length: ax25_frame.payload.ax25_info.length
    :field time_unix: ax25_frame.payload.ax25_info.time_unix
    :field vbatt: ax25_frame.payload.ax25_info.service.sub_service.vbatt
    :field batt_current: ax25_frame.payload.ax25_info.service.sub_service.batt_current
    :field current3v3: ax25_frame.payload.ax25_info.service.sub_service.current3v3
    :field current5v: ax25_frame.payload.ax25_info.service.sub_service.current5v
    :field lotrxvu_temp: ax25_frame.payload.ax25_info.service.sub_service.lotrxvu_temp
    :field patrxvu_temp: ax25_frame.payload.ax25_info.service.sub_service.patrxvu_temp
    :field eps_temp_1: ax25_frame.payload.ax25_info.service.sub_service.eps_temp_1
    :field eps_temp_2: ax25_frame.payload.ax25_info.service.sub_service.eps_temp_2
    :field eps_temp_3: ax25_frame.payload.ax25_info.service.sub_service.eps_temp_3
    :field eps_temp_4: ax25_frame.payload.ax25_info.service.sub_service.eps_temp_4
    :field batt_temp_1: ax25_frame.payload.ax25_info.service.sub_service.batt_temp_1
    :field batt_temp_2: ax25_frame.payload.ax25_info.service.sub_service.batt_temp_2
    :field rx_doppler: ax25_frame.payload.ax25_info.service.sub_service.rx_doppler
    :field rxrssi: ax25_frame.payload.ax25_info.service.sub_service.rxrssi
    :field txrefl: ax25_frame.payload.ax25_info.service.sub_service.txrefl
    :field txforw: ax25_frame.payload.ax25_info.service.sub_service.txforw
    :field altitude_angels_roll: ax25_frame.payload.ax25_info.service.sub_service.altitude_angels_roll
    :field altitude_angels_pitch: ax25_frame.payload.ax25_info.service.sub_service.altitude_angels_pitch
    :field altitude_angels_yaw: ax25_frame.payload.ax25_info.service.sub_service.altitude_angels_yaw
    :field file_system_last_error: ax25_frame.payload.ax25_info.service.sub_service.file_system_last_error
    :field eps_battery_state: ax25_frame.payload.ax25_info.service.sub_service.eps_battery_state
    :field delayed_commands_num: ax25_frame.payload.ax25_info.service.sub_service.delayed_commands_num
    :field resets_num: ax25_frame.payload.ax25_info.service.sub_service.resets_num
    :field last_reset: ax25_frame.payload.ax25_info.service.sub_service.last_reset
    :field system_states: ax25_frame.payload.ax25_info.service.sub_service.system_states
    :field event_log_num: ax25_frame.payload.ax25_info.service.sub_service.event_log_num
    :field event_log_info: ax25_frame.payload.ax25_info.service.sub_service.event_log_info
    :field error_log_num: ax25_frame.payload.ax25_info.service.sub_service.error_log_num
    :field error_log_info: ax25_frame.payload.ax25_info.service.sub_service.error_log_info
    :field photo_voltaic_3: ax25_frame.payload.ax25_info.service.sub_service.photo_voltaic_3
    :field photo_voltaic_2: ax25_frame.payload.ax25_info.service.sub_service.photo_voltaic_2
    :field photo_voltaic_1: ax25_frame.payload.ax25_info.service.sub_service.photo_voltaic_1
    :field photo_current_3: ax25_frame.payload.ax25_info.service.sub_service.photo_current_3
    :field photo_current_2: ax25_frame.payload.ax25_info.service.sub_service.photo_current_2
    :field photo_current_1: ax25_frame.payload.ax25_info.service.sub_service.photo_current_1
    :field photo_current_total: ax25_frame.payload.ax25_info.service.sub_service.photo_current_total
    :field batt_current_3: ax25_frame.payload.ax25_info.service.sub_service.batt_current_3
    :field channel_current_1: ax25_frame.payload.ax25_info.service.sub_service.channel_current_1
    :field channel_current_2: ax25_frame.payload.ax25_info.service.sub_service.channel_current_2
    :field channel_current_3: ax25_frame.payload.ax25_info.service.sub_service.channel_current_3
    :field channel_current_4: ax25_frame.payload.ax25_info.service.sub_service.channel_current_4
    :field channel_current_5: ax25_frame.payload.ax25_info.service.sub_service.channel_current_5
    :field channel_current_6: ax25_frame.payload.ax25_info.service.sub_service.channel_current_6
    :field eps_reboots_num: ax25_frame.payload.ax25_info.service.sub_service.eps_reboots_num
    :field eps_reboot_cause: ax25_frame.payload.ax25_info.service.sub_service.eps_reboot_cause
    :field eps_ppt_mode: ax25_frame.payload.ax25_info.service.sub_service.eps_ppt_mode
    :field eps_channel_status: ax25_frame.payload.ax25_info.service.sub_service.eps_channel_status
    :field system_states: ax25_frame.payload.ax25_info.service.sub_service.system_states
    :field trxvu_bus_volt: ax25_frame.payload.ax25_info.service.sub_service.trxvu_bus_volt
    :field trxvu_total_curr: ax25_frame.payload.ax25_info.service.sub_service.trxvu_total_curr
    :field ant_temp_a: ax25_frame.payload.ax25_info.service.sub_service.ant_temp_a
    :field ant_temp_b: ax25_frame.payload.ax25_info.service.sub_service.ant_temp_b
    :field sp_temp_1: ax25_frame.payload.ax25_info.service.sub_service.sp_temp_1
    :field sp_temp_2: ax25_frame.payload.ax25_info.service.sub_service.sp_temp_2
    :field sp_temp_3: ax25_frame.payload.ax25_info.service.sub_service.sp_temp_3
    :field sp_temp_4: ax25_frame.payload.ax25_info.service.sub_service.sp_temp_4
    :field sp_temp_5: ax25_frame.payload.ax25_info.service.sub_service.sp_temp_5
    :field sp_temp_6: ax25_frame.payload.ax25_info.service.sub_service.sp_temp_6
    :field filesystem_a_total: ax25_frame.payload.ax25_info.service.sub_service.filesystem_a_total
    :field filesystem_a_free: ax25_frame.payload.ax25_info.service.sub_service.filesystem_a_free
    :field filesystem_a_used: ax25_frame.payload.ax25_info.service.sub_service.filesystem_a_used
    :field filesystem_a_bad: ax25_frame.payload.ax25_info.service.sub_service.filesystem_a_bad
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Duchifat3.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Duchifat3.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Duchifat3.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Duchifat3.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Duchifat3.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Duchifat3.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Duchifat3.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Duchifat3.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Duchifat3.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Duchifat3.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Duchifat3.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Duchifat3.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Duchifat3.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class EventLogT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.event_log_num = self._io.read_u4le()
            self.event_log_info = self._io.read_u4le()


    class FileSystemSpaceAT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.filesystem_a_total = self._io.read_u4le()
            self.filesystem_a_free = self._io.read_u4le()
            self.filesystem_a_used = self._io.read_u4le()
            self.filesystem_a_bad = self._io.read_u4le()


    class EpsTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.photo_voltaic_3 = self._io.read_u2le()
            self.photo_voltaic_2 = self._io.read_u2le()
            self.photo_voltaic_1 = self._io.read_u2le()
            self.photo_current_3 = self._io.read_u2le()
            self.photo_current_2 = self._io.read_u2le()
            self.photo_current_1 = self._io.read_u2le()
            self.photo_current_total = self._io.read_u2le()
            self.vbatt = self._io.read_u2le()
            self.batt_current_3 = self._io.read_u2le()
            self.channel_current_1 = self._io.read_u2le()
            self.channel_current_2 = self._io.read_u2le()
            self.channel_current_3 = self._io.read_u2le()
            self.channel_current_4 = self._io.read_u2le()
            self.channel_current_5 = self._io.read_u2le()
            self.channel_current_6 = self._io.read_u2le()
            self.eps_temp_1 = self._io.read_s2le()
            self.eps_temp_2 = self._io.read_s2le()
            self.eps_temp_3 = self._io.read_s2le()
            self.eps_temp_4 = self._io.read_s2le()
            self.batt_temp_1 = self._io.read_s2le()
            self.batt_temp_2 = self._io.read_s2le()
            self.eps_reboots_num = self._io.read_u4le()
            self.eps_reboot_cause = self._io.read_u1()
            self.eps_ppt_mode = self._io.read_u1()
            self.eps_channel_status = self._io.read_u1()
            self.system_states = self._io.read_u1()
            self.eps_battery_state = self._io.read_u1()


    class TelemetryDumpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.sub_service_type
            if _on == 50:
                self.sub_service = Duchifat3.EpsTlmT(self._io, self, self._root)
            elif _on == 51:
                self.sub_service = Duchifat3.CommTlmT(self._io, self, self._root)
            elif _on == 53:
                self.sub_service = Duchifat3.SolarPanelsTlmT(self._io, self, self._root)
            elif _on == 73:
                self.sub_service = Duchifat3.FileSystemSpaceAT(self._io, self, self._root)


    class BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vbatt = self._io.read_u2be()
            self.batt_current = self._io.read_u2be()
            self.current3v3 = self._io.read_u2be()
            self.current5v = self._io.read_u2be()
            self.lotrxvu_temp = self._io.read_u2be()
            self.patrxvu_temp = self._io.read_u2be()
            self.eps_temp_1 = self._io.read_s2be()
            self.eps_temp_2 = self._io.read_s2be()
            self.eps_temp_3 = self._io.read_s2be()
            self.eps_temp_4 = self._io.read_s2be()
            self.batt_temp_1 = self._io.read_s2be()
            self.batt_temp_2 = self._io.read_s2be()
            self.rx_doppler = self._io.read_u2be()
            self.rxrssi = self._io.read_u2be()
            self.txrefl = self._io.read_u2be()
            self.txforw = self._io.read_u2be()
            self.altitude_angels_roll = self._io.read_s2be()
            self.altitude_angels_pitch = self._io.read_s2be()
            self.altitude_angels_yaw = self._io.read_s2be()
            self.file_system_last_error = self._io.read_u1()
            self.eps_battery_state = self._io.read_u1()
            self.delayed_commands_num = self._io.read_u1()
            self.resets_num = self._io.read_u4be()
            self.last_reset = self._io.read_u4be()
            self.system_states = self._io.read_u1()


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Duchifat3.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class CommTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.trxvu_bus_volt = self._io.read_u2le()
            self.trxvu_total_curr = self._io.read_u2le()
            self.txrefl = self._io.read_u2le()
            self.txforw = self._io.read_u2le()
            self.rxrssi = self._io.read_u2le()
            self.patrxvu_temp = self._io.read_u2le()
            self.lotrxvu_temp = self._io.read_u2le()
            self.ant_temp_a = self._io.read_u2le()
            self.ant_temp_b = self._io.read_u2le()


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


    class ErrorLogT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.error_log_num = self._io.read_u4le()
            self.error_log_info = self._io.read_u4le()


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Duchifat3.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Duchifat3.SsidMask(self._io, self, self._root)


    class Repeater(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_instance = []
            i = 0
            while True:
                _ = Duchifat3.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class GeneralT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.sub_service_type
            if _on == 49:
                self.sub_service = Duchifat3.EventLogT(self._io, self, self._root)
            elif _on == 50:
                self.sub_service = Duchifat3.ErrorLogT(self._io, self, self._root)


    class SolarPanelsTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sp_temp_1 = self._io.read_s4le()
            self.sp_temp_2 = self._io.read_s4le()
            self.sp_temp_3 = self._io.read_s4le()
            self.sp_temp_4 = self._io.read_s4le()
            self.sp_temp_5 = self._io.read_s4le()
            self.sp_temp_6 = self._io.read_s4le()


    class GlobalParametersT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.sub_service_type
            if _on == 25:
                self.sub_service = Duchifat3.BeaconT(self._io, self, self._root)


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
            self.callsign_ror = Duchifat3.Callsign(_io__raw_callsign_ror, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.service_type = self._io.read_u1()
            self.sub_service_type = self._io.read_u1()
            self.length = self._io.read_u2be()
            self.time_unix = self._io.read_u4be()
            _on = self.service_type
            if _on == 3:
                self.service = Duchifat3.GlobalParametersT(self._io, self, self._root)
            elif _on == 13:
                self.service = Duchifat3.GeneralT(self._io, self, self._root)
            elif _on == 88:
                self.service = Duchifat3.TelemetryDumpsT(self._io, self, self._root)



