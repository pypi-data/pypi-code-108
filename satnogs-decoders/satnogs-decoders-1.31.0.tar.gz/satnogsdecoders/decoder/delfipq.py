# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Delfipq(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packet: ax25_frame.payload.ax25_info.packet
    :field destination: ax25_frame.payload.ax25_info.delfipq.destination
    :field size: ax25_frame.payload.ax25_info.delfipq.size
    :field beacon_source: ax25_frame.payload.ax25_info.delfipq.beacon_source
    :field service: ax25_frame.payload.ax25_info.delfipq.service
    :field message_type: ax25_frame.payload.ax25_info.delfipq.message_type
    :field message_outcome: ax25_frame.payload.ax25_info.delfipq.message_outcome
    :field tlm_source: ax25_frame.payload.ax25_info.delfipq.tlm_source
    :field pad: ax25_frame.payload.ax25_info.delfipq.telemetry_header.status.pad
    :field software_image: ax25_frame.payload.ax25_info.delfipq.telemetry_header.status.software_image
    :field boot_counter: ax25_frame.payload.ax25_info.delfipq.telemetry_header.boot_counter
    :field soft_reset_wdt_timerexpiration: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.soft_reset_wdt_timerexpiration
    :field cpu_lock_up: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.cpu_lock_up
    :field por_power_settle: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.por_power_settle
    :field por_clock_settle: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.por_clock_settle
    :field voltage_anomaly: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.voltage_anomaly
    :field hard_reset_wdt_wrong_password: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.hard_reset_wdt_wrong_password
    :field hard_reset_wdt_timerexpiration: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.hard_reset_wdt_timerexpiration
    :field system_reset_output: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.system_reset_output
    :field sys_ctl_reboot: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.sys_ctl_reboot
    :field nmi_pin: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.nmi_pin
    :field exit_lpm4p5: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.exit_lpm4p5
    :field exit_lpm3p5: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.exit_lpm3p5
    :field bad_band_gap_reference: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.bad_band_gap_reference
    :field supply_supervisor_vcc_trip: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.supply_supervisor_vcc_trip
    :field vcc_detector_trip: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.vcc_detector_trip
    :field soft_reset_wdt_wrong_password: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.soft_reset_wdt_wrong_password
    :field padding: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.padding
    :field dco_short_circuit_fault: ax25_frame.payload.ax25_info.delfipq.telemetry_header.reset_cause.dco_short_circuit_fault
    :field uptime: ax25_frame.payload.ax25_info.delfipq.telemetry_header.uptime
    :field total_uptime: ax25_frame.payload.ax25_info.delfipq.telemetry_header.total_uptime
    :field tlm_version: ax25_frame.payload.ax25_info.delfipq.telemetry_header.tlm_version
    :field mcu_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mcu_temperature
    :field ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.sensors_status.ina_status
    :field tmp_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.sensors_status.tmp_status
    :field telemetry_sensors_status_padding: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.sensors_status.padding
    :field bus_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus_voltage
    :field bus_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus_current
    :field battery_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.battery_ina_status
    :field battery_gg_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.battery_gg_status
    :field internal_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.internal_ina_status
    :field unregulated_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.unregulated_ina_status
    :field bus1_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus1_ina_status
    :field bus2_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus2_ina_status
    :field bus3_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus3_ina_status
    :field bus4_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus4_ina_status
    :field bus4_error: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus4_error
    :field bus3_error: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus3_error
    :field bus2_error: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus2_error
    :field bus1_error: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus1_error
    :field bus4_state: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus4_state
    :field bus3_state: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus3_state
    :field bus2_state: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus2_state
    :field bus1_state: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.bus1_state
    :field panel_yp_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_yp_ina_status
    :field panel_ym_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_ym_ina_status
    :field panel_xp_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_xp_ina_status
    :field panel_xm_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_xm_ina_status
    :field panel_yp_tmp_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_yp_tmp_status
    :field panel_ym_tmp_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_ym_tmp_status
    :field panel_xp_tmp_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_xp_tmp_status
    :field panel_xm_tmp_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.panel_xm_tmp_status
    :field mppt_yp_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.mppt_yp_ina_status
    :field mppt_ym_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.mppt_ym_ina_status
    :field mppt_xp_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.mppt_xp_ina_status
    :field mppt_xm_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.mppt_xm_ina_status
    :field cell_yp_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.cell_yp_ina_status
    :field cell_ym_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.cell_ym_ina_status
    :field cell_xp_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.cell_xp_ina_status
    :field cell_xm_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.status.cell_xm_ina_status
    :field internal_ina_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.internal_ina_current
    :field internal_ina_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.internal_ina_voltage
    :field unregulated_ina_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.unregulated_ina_current
    :field unregulated_ina_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.unregulated_ina_voltage
    :field battery_gg_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.battery_gg_voltage
    :field battery_ina_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.battery_ina_voltage
    :field battery_ina_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.battery_ina_current
    :field battery_gg_capacity: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.battery_gg_capacity
    :field battery_gg_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.battery_gg_temperature
    :field battery_tmp20_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.battery_tmp20_temperature
    :field bus4_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus4_current
    :field bus3_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus3_current
    :field bus2_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus2_current
    :field bus1_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus1_current
    :field bus4_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus4_voltage
    :field bus3_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus3_voltage
    :field bus2_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus2_voltage
    :field bus1_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.bus1_voltage
    :field panel_yp_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_yp_current
    :field panel_ym_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_ym_current
    :field panel_xp_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_xp_current
    :field panel_xm_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_xm_current
    :field panel_yp_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_yp_voltage
    :field panel_ym_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_ym_voltage
    :field panel_xp_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_xp_voltage
    :field panel_xm_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_xm_voltage
    :field panel_yp_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_yp_temperature
    :field panel_ym_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_ym_temperature
    :field panel_xp_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_xp_temperature
    :field panel_xm_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.panel_xm_temperature
    :field mppt_yp_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_yp_current
    :field mppt_ym_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_ym_current
    :field mppt_xp_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_xp_current
    :field mppt_xm_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_xm_current
    :field mppt_yp_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_yp_voltage
    :field mppt_ym_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_ym_voltage
    :field mppt_xp_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_xp_voltage
    :field mppt_xm_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.mppt_xm_voltage
    :field cell_yp_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.cell_yp_current
    :field cell_ym_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.cell_ym_current
    :field cell_xp_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.cell_xp_current
    :field cell_xm_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.cell_xm_current
    :field cell_yp_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.cell_yp_voltage
    :field cell_ym_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.cell_ym_voltage
    :field cell_xp_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.cell_xp_voltage
    :field current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.current
    :field voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.voltage
    :field temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.temperature
    :field transmit_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.sensors_status.transmit_ina_status
    :field amplifier_ina_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.sensors_status.amplifier_ina_status
    :field phasing_tmp_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.sensors_status.phasing_tmp_status
    :field amplifier_tmp_status: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.sensors_status.amplifier_tmp_status
    :field receiver_rssi: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.receiver_rssi
    :field transmit_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.transmit_voltage
    :field transmit_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.transmit_current
    :field amplifier_voltage: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.amplifier_voltage
    :field amplifier_current: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.amplifier_current
    :field phasing_board_temperature: ax25_frame.payload.ax25_info.delfipq.telemetry_header.telemetry.phasing_board_temperature
    :field frametype: frametype
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Delfipq.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Delfipq.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Delfipq.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Delfipq.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Delfipq.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Delfipq.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Delfipq.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Delfipq.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Delfipq.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Delfipq.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Delfipq.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Delfipq.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Delfipq.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class Epstlmv2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mcu_temperature = self._io.read_s2be()
            self.status = Delfipq.EpsSensorStatusT(self._io, self, self._root)
            self.internal_ina_current = self._io.read_s2be()
            self.internal_ina_voltage = self._io.read_u2be()
            self.unregulated_ina_current = self._io.read_s2be()
            self.unregulated_ina_voltage = self._io.read_u2be()
            self.battery_gg_voltage = self._io.read_u2be()
            self.battery_ina_voltage = self._io.read_u2be()
            self.battery_ina_current = self._io.read_s2be()
            self.battery_gg_capacity = self._io.read_u2be()
            self.battery_gg_temperature = self._io.read_s2be()
            self.battery_tmp20_temperature = self._io.read_s2be()
            self.bus4_current = self._io.read_s2be()
            self.bus3_current = self._io.read_s2be()
            self.bus2_current = self._io.read_s2be()
            self.bus1_current = self._io.read_s2be()
            self.bus4_voltage = self._io.read_u2be()
            self.bus3_voltage = self._io.read_u2be()
            self.bus2_voltage = self._io.read_u2be()
            self.bus1_voltage = self._io.read_u2be()
            self.panel_yp_current = self._io.read_s2be()
            self.panel_ym_current = self._io.read_s2be()
            self.panel_xp_current = self._io.read_s2be()
            self.panel_xm_current = self._io.read_s2be()
            self.panel_yp_voltage = self._io.read_u2be()
            self.panel_ym_voltage = self._io.read_u2be()
            self.panel_xp_voltage = self._io.read_u2be()
            self.panel_xm_voltage = self._io.read_u2be()
            self.panel_yp_temperature = self._io.read_s2be()
            self.panel_ym_temperature = self._io.read_s2be()
            self.panel_xp_temperature = self._io.read_s2be()
            self.panel_xm_temperature = self._io.read_s2be()
            self.mppt_yp_current = self._io.read_s2be()
            self.mppt_ym_current = self._io.read_s2be()
            self.mppt_xp_current = self._io.read_s2be()
            self.mppt_xm_current = self._io.read_s2be()
            self.mppt_yp_voltage = self._io.read_u2be()
            self.mppt_ym_voltage = self._io.read_u2be()
            self.mppt_xp_voltage = self._io.read_u2be()
            self.mppt_xm_voltage = self._io.read_u2be()
            self.cell_yp_current = self._io.read_s2be()
            self.cell_ym_current = self._io.read_s2be()
            self.cell_xp_current = self._io.read_s2be()
            self.cell_xm_current = self._io.read_s2be()
            self.cell_yp_voltage = self._io.read_u2be()
            self.cell_ym_voltage = self._io.read_u2be()
            self.cell_xp_voltage = self._io.read_u2be()


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
            self.ax25_info = Delfipq.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"GROUND") or (self.callsign == u"DLFIPQ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class Obctlmv2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mcu_temperature = self._io.read_s2be()
            self.sensors_status = Delfipq.ObcSensorStatusT(self._io, self, self._root)
            self.bus_voltage = self._io.read_u2be()
            self.bus_current = self._io.read_s2be()


    class CommstlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status = Delfipq.SubsystemStatusT(self._io, self, self._root)
            self.boot_counter = self._io.read_u1()
            self.reset_cause = Delfipq.ResetCauseT(self._io, self, self._root)
            self.uptime = self._io.read_u4be()
            self.total_uptime = self._io.read_u4be()
            self.tlm_version = self._io.read_u1()
            _on = self.tlm_version
            if _on == 2:
                self.telemetry = Delfipq.Commstlmv2T(self._io, self, self._root)


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
            self.ax25_info = Delfipq.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class ResetCauseT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.soft_reset_wdt_timerexpiration = self._io.read_bits_int_be(1) != 0
            self.cpu_lock_up = self._io.read_bits_int_be(1) != 0
            self.por_power_settle = self._io.read_bits_int_be(1) != 0
            self.por_clock_settle = self._io.read_bits_int_be(1) != 0
            self.voltage_anomaly = self._io.read_bits_int_be(1) != 0
            self.hard_reset_wdt_wrong_password = self._io.read_bits_int_be(1) != 0
            self.hard_reset_wdt_timerexpiration = self._io.read_bits_int_be(1) != 0
            self.system_reset_output = self._io.read_bits_int_be(1) != 0
            self.sys_ctl_reboot = self._io.read_bits_int_be(1) != 0
            self.nmi_pin = self._io.read_bits_int_be(1) != 0
            self.exit_lpm4p5 = self._io.read_bits_int_be(1) != 0
            self.exit_lpm3p5 = self._io.read_bits_int_be(1) != 0
            self.bad_band_gap_reference = self._io.read_bits_int_be(1) != 0
            self.supply_supervisor_vcc_trip = self._io.read_bits_int_be(1) != 0
            self.vcc_detector_trip = self._io.read_bits_int_be(1) != 0
            self.soft_reset_wdt_wrong_password = self._io.read_bits_int_be(1) != 0
            self.padding = self._io.read_bits_int_be(7)
            self.dco_short_circuit_fault = self._io.read_bits_int_be(1) != 0


    class CommsSensorStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ina_status = self._io.read_bits_int_be(1) != 0
            self.tmp_status = self._io.read_bits_int_be(1) != 0
            self.transmit_ina_status = self._io.read_bits_int_be(1) != 0
            self.amplifier_ina_status = self._io.read_bits_int_be(1) != 0
            self.phasing_tmp_status = self._io.read_bits_int_be(1) != 0
            self.amplifier_tmp_status = self._io.read_bits_int_be(1) != 0
            self.padding = self._io.read_bits_int_be(2)


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Delfipq.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Delfipq.SsidMask(self._io, self, self._root)


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
                _ = Delfipq.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class SubsystemStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pad = self._io.read_bits_int_be(4)
            self.software_image = self._io.read_bits_int_be(4)


    class AdbtlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status = Delfipq.SubsystemStatusT(self._io, self, self._root)
            self.boot_counter = self._io.read_u1()
            self.reset_cause = Delfipq.ResetCauseT(self._io, self, self._root)
            self.uptime = self._io.read_u4be()
            self.total_uptime = self._io.read_u4be()
            self.tlm_version = self._io.read_u1()
            _on = self.tlm_version
            if _on == 2:
                self.telemetry = Delfipq.Adbtlmv2T(self._io, self, self._root)


    class Commstlmv2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mcu_temperature = self._io.read_s2be()
            self.sensors_status = Delfipq.CommsSensorStatusT(self._io, self, self._root)
            self.voltage = self._io.read_u2be()
            self.current = self._io.read_s2be()
            self.temperature = self._io.read_s2be()
            self.receiver_rssi = self._io.read_s2be()
            self.transmit_voltage = self._io.read_u2be()
            self.transmit_current = self._io.read_s2be()
            self.amplifier_voltage = self._io.read_u2be()
            self.amplifier_current = self._io.read_s2be()
            self.phasing_board_temperature = self._io.read_s2be()


    class ObctlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status = Delfipq.SubsystemStatusT(self._io, self, self._root)
            self.boot_counter = self._io.read_u1()
            self.reset_cause = Delfipq.ResetCauseT(self._io, self, self._root)
            self.uptime = self._io.read_u4be()
            self.total_uptime = self._io.read_u4be()
            self.tlm_version = self._io.read_u1()
            _on = self.tlm_version
            if _on == 2:
                self.telemetry = Delfipq.Obctlmv2T(self._io, self, self._root)


    class Adbtlmv2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mcu_temperature = self._io.read_s2be()
            self.sensors_status = Delfipq.AdbSensorStatusT(self._io, self, self._root)
            self.current = self._io.read_s2be()
            self.voltage = self._io.read_u2be()
            self.temperature = self._io.read_s2be()


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
            self.callsign_ror = Delfipq.Callsign(_io__raw_callsign_ror, self, self._root)


    class DelfipqBeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.destination = self._io.read_u1()
            self.size = self._io.read_u1()
            self.beacon_source = self._io.read_u1()
            self.service = self._io.read_u1()
            self.message_type = self._io.read_u1()
            self.message_outcome = self._io.read_u1()
            self.tlm_source = self._io.read_u1()
            _on = self.tlm_source
            if _on == 1:
                self.telemetry_header = Delfipq.ObctlmT(self._io, self, self._root)
            elif _on == 2:
                self.telemetry_header = Delfipq.EpstlmT(self._io, self, self._root)
            elif _on == 3:
                self.telemetry_header = Delfipq.AdbtlmT(self._io, self, self._root)
            elif _on == 4:
                self.telemetry_header = Delfipq.CommstlmT(self._io, self, self._root)


    class EpsSensorStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_ina_status = self._io.read_bits_int_be(1) != 0
            self.battery_gg_status = self._io.read_bits_int_be(1) != 0
            self.internal_ina_status = self._io.read_bits_int_be(1) != 0
            self.unregulated_ina_status = self._io.read_bits_int_be(1) != 0
            self.bus1_ina_status = self._io.read_bits_int_be(1) != 0
            self.bus2_ina_status = self._io.read_bits_int_be(1) != 0
            self.bus3_ina_status = self._io.read_bits_int_be(1) != 0
            self.bus4_ina_status = self._io.read_bits_int_be(1) != 0
            self.bus4_error = self._io.read_bits_int_be(1) != 0
            self.bus3_error = self._io.read_bits_int_be(1) != 0
            self.bus2_error = self._io.read_bits_int_be(1) != 0
            self.bus1_error = self._io.read_bits_int_be(1) != 0
            self.bus4_state = self._io.read_bits_int_be(1) != 0
            self.bus3_state = self._io.read_bits_int_be(1) != 0
            self.bus2_state = self._io.read_bits_int_be(1) != 0
            self.bus1_state = self._io.read_bits_int_be(1) != 0
            self.panel_yp_ina_status = self._io.read_bits_int_be(1) != 0
            self.panel_ym_ina_status = self._io.read_bits_int_be(1) != 0
            self.panel_xp_ina_status = self._io.read_bits_int_be(1) != 0
            self.panel_xm_ina_status = self._io.read_bits_int_be(1) != 0
            self.panel_yp_tmp_status = self._io.read_bits_int_be(1) != 0
            self.panel_ym_tmp_status = self._io.read_bits_int_be(1) != 0
            self.panel_xp_tmp_status = self._io.read_bits_int_be(1) != 0
            self.panel_xm_tmp_status = self._io.read_bits_int_be(1) != 0
            self.mppt_yp_ina_status = self._io.read_bits_int_be(1) != 0
            self.mppt_ym_ina_status = self._io.read_bits_int_be(1) != 0
            self.mppt_xp_ina_status = self._io.read_bits_int_be(1) != 0
            self.mppt_xm_ina_status = self._io.read_bits_int_be(1) != 0
            self.cell_yp_ina_status = self._io.read_bits_int_be(1) != 0
            self.cell_ym_ina_status = self._io.read_bits_int_be(1) != 0
            self.cell_xp_ina_status = self._io.read_bits_int_be(1) != 0
            self.cell_xm_ina_status = self._io.read_bits_int_be(1) != 0


    class ObcSensorStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ina_status = self._io.read_bits_int_be(1) != 0
            self.tmp_status = self._io.read_bits_int_be(1) != 0
            self.padding = self._io.read_bits_int_be(6)


    class AdbSensorStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ina_status = self._io.read_bits_int_be(1) != 0
            self.tmp_status = self._io.read_bits_int_be(1) != 0
            self.padding = self._io.read_bits_int_be(6)


    class EpstlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status = Delfipq.SubsystemStatusT(self._io, self, self._root)
            self.boot_counter = self._io.read_u1()
            self.reset_cause = Delfipq.ResetCauseT(self._io, self, self._root)
            self.uptime = self._io.read_u4be()
            self.total_uptime = self._io.read_u4be()
            self.tlm_version = self._io.read_u1()
            _on = self.tlm_version
            if _on == 2:
                self.telemetry = Delfipq.Epstlmv2T(self._io, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet = self._io.read_u1()
            _on = self.packet
            if _on == 0:
                self._raw_delfipq = self._io.read_bytes_full()
                _io__raw_delfipq = KaitaiStream(BytesIO(self._raw_delfipq))
                self.delfipq = Delfipq.DelfipqBeaconT(_io__raw_delfipq, self, self._root)
            else:
                self.delfipq = self._io.read_bytes_full()


    @property
    def frametype(self):
        if hasattr(self, '_m_frametype'):
            return self._m_frametype if hasattr(self, '_m_frametype') else None

        _pos = self._io.pos()
        self._io.seek(16)
        self._m_frametype = self._io.read_u1()
        self._io.seek(_pos)
        return self._m_frametype if hasattr(self, '_m_frametype') else None


