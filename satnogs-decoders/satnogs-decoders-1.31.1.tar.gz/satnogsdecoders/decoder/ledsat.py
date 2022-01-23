# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Ledsat(KaitaiStruct):
    """:field priority: csp_header.priority
    :field source: csp_header.source
    :field destination: csp_header.destination
    :field destination_port: csp_header.destination_port
    :field source_port: csp_header.source_port
    :field reserved: csp_header.reserved
    :field hmac: csp_header.hmac
    :field xtea: csp_header.xtea
    :field rdp: csp_header.rdp
    :field crc: csp_header.crc
    :field telemetry_identifier: csp_data.payload.telemetry_identifier
    :field unix_ts_ms: csp_data.payload.unix_ts_ms
    :field unix_ts_s: csp_data.payload.unix_ts_s
    :field tlm_process_time: csp_data.payload.tlm_process_time
    :field panel_x_voltage: csp_data.payload.panel_x_voltage
    :field panel_y_voltage: csp_data.payload.panel_y_voltage
    :field panel_z_voltage: csp_data.payload.panel_z_voltage
    :field panel_x_current: csp_data.payload.panel_x_current
    :field panel_y_current: csp_data.payload.panel_y_current
    :field panel_z_current: csp_data.payload.panel_z_current
    :field eps_boot_cause: csp_data.payload.eps_boot_cause
    :field eps_battery_mode: csp_data.payload.eps_battery_mode
    :field mppt_x_temp: csp_data.payload.mppt_x_temp
    :field mppt_y_temp: csp_data.payload.mppt_y_temp
    :field eps_board_temp: csp_data.payload.eps_board_temp
    :field battery_pack1_temp: csp_data.payload.battery_pack1_temp
    :field battery_pack2_temp: csp_data.payload.battery_pack2_temp
    :field battery_pack3_temp: csp_data.payload.battery_pack3_temp
    :field solar_current: csp_data.payload.solar_current
    :field system_current: csp_data.payload.system_current
    :field battery_voltage: csp_data.payload.battery_voltage
    :field gps_current: csp_data.payload.gps_current
    :field eps_boot_count: csp_data.payload.eps_boot_count
    :field trx_pa_temp: csp_data.payload.trx_pa_temp
    :field trx_total_tx_cnt: csp_data.payload.trx_total_tx_cnt
    :field trx_total_rx_cnt: csp_data.payload.trx_total_rx_cnt
    :field last_rssi: csp_data.payload.last_rssi
    :field radio_boot_cnt: csp_data.payload.radio_boot_cnt
    :field obc_temp_1: csp_data.payload.obc_temp_1
    :field obc_temp_2: csp_data.payload.obc_temp_2
    :field gyro_x: csp_data.payload.gyro_x
    :field gyro_y: csp_data.payload.gyro_y
    :field gyro_z: csp_data.payload.gyro_z
    :field mag_x: csp_data.payload.mag_x
    :field mag_y: csp_data.payload.mag_y
    :field mag_z: csp_data.payload.mag_z
    :field px_solar_panel_temp: csp_data.payload.px_solar_panel_temp
    :field py_solar_panel_temp: csp_data.payload.py_solar_panel_temp
    :field nx_solar_panel_temp: csp_data.payload.nx_solar_panel_temp
    :field ny_solar_panel_temp: csp_data.payload.ny_solar_panel_temp
    :field pz_solar_panel_temp: csp_data.payload.pz_solar_panel_temp
    :field nz_solar_panel_temp: csp_data.payload.nz_solar_panel_temp
    :field px_sun_sensor_coarse: csp_data.payload.px_sun_sensor_coarse
    :field py_sun_sensor_coarse: csp_data.payload.py_sun_sensor_coarse
    :field pz_sun_sensor_coarse: csp_data.payload.pz_sun_sensor_coarse
    :field nx_sun_sensor_coarse: csp_data.payload.nx_sun_sensor_coarse
    :field ny_sun_sensor_coarse: csp_data.payload.ny_sun_sensor_coarse
    :field nz_sun_sensor_coarse: csp_data.payload.nz_sun_sensor_coarse
    :field eps_outputs_status: csp_data.payload.eps_outputs_status
    :field obc_boot_counter: csp_data.payload.obc_boot_counter
    :field leds_status: csp_data.payload.leds_status
    :field gps_status: csp_data.payload.gps_status
    :field gps_fix_time: csp_data.payload.gps_fix_time
    :field gps_lat: csp_data.payload.gps_lat
    :field gps_lon: csp_data.payload.gps_lon
    :field gps_alt: csp_data.payload.gps_alt
    :field software_status: csp_data.payload.software_status
    :field ext_gyro_x: csp_data.payload.ext_gyro_x
    :field ext_gyro_y: csp_data.payload.ext_gyro_y
    :field ext_gyro_z: csp_data.payload.ext_gyro_z
    :field ext_mag_x: csp_data.payload.ext_mag_x
    :field ext_mag_y: csp_data.payload.ext_mag_y
    :field ext_mag_z: csp_data.payload.ext_mag_z
    :field framelength: framelength
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.csp_header = Ledsat.CspHeaderT(self._io, self, self._root)
        self.csp_data = Ledsat.CspDataT(self._io, self, self._root)

    class CspHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw_csp_header = self._io.read_u4be()

        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source if hasattr(self, '_m_source') else None

            self._m_source = ((self.raw_csp_header >> 25) & 31)
            return self._m_source if hasattr(self, '_m_source') else None

        @property
        def source_port(self):
            if hasattr(self, '_m_source_port'):
                return self._m_source_port if hasattr(self, '_m_source_port') else None

            self._m_source_port = ((self.raw_csp_header >> 8) & 63)
            return self._m_source_port if hasattr(self, '_m_source_port') else None

        @property
        def destination_port(self):
            if hasattr(self, '_m_destination_port'):
                return self._m_destination_port if hasattr(self, '_m_destination_port') else None

            self._m_destination_port = ((self.raw_csp_header >> 14) & 63)
            return self._m_destination_port if hasattr(self, '_m_destination_port') else None

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp if hasattr(self, '_m_rdp') else None

            self._m_rdp = ((self.raw_csp_header & 2) >> 1)
            return self._m_rdp if hasattr(self, '_m_rdp') else None

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination if hasattr(self, '_m_destination') else None

            self._m_destination = ((self.raw_csp_header >> 20) & 31)
            return self._m_destination if hasattr(self, '_m_destination') else None

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority if hasattr(self, '_m_priority') else None

            self._m_priority = (self.raw_csp_header >> 30)
            return self._m_priority if hasattr(self, '_m_priority') else None

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved if hasattr(self, '_m_reserved') else None

            self._m_reserved = ((self.raw_csp_header >> 4) & 15)
            return self._m_reserved if hasattr(self, '_m_reserved') else None

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea if hasattr(self, '_m_xtea') else None

            self._m_xtea = ((self.raw_csp_header & 4) >> 2)
            return self._m_xtea if hasattr(self, '_m_xtea') else None

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac if hasattr(self, '_m_hmac') else None

            self._m_hmac = ((self.raw_csp_header & 8) >> 3)
            return self._m_hmac if hasattr(self, '_m_hmac') else None

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc if hasattr(self, '_m_crc') else None

            self._m_crc = (self.raw_csp_header & 1)
            return self._m_crc if hasattr(self, '_m_crc') else None


    class CspDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.csp_header.destination_port
            if _on == 8:
                self.payload = Ledsat.LedsatTlmT(self._io, self, self._root)


    class LedsatTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.telemetry_identifier = self._io.read_u2be()
            if not  ((self.telemetry_identifier == 5672) or (self.telemetry_identifier == 5673) or (self.telemetry_identifier == 5674)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.telemetry_identifier, self._io, u"/types/ledsat_tlm_t/seq/0")
            self.unix_ts_ms = self._io.read_u2be()
            self.unix_ts_s = self._io.read_u4be()
            self.tlm_process_time = self._io.read_u2be()
            self.panel_x_voltage = self._io.read_u2be()
            self.panel_y_voltage = self._io.read_u2be()
            self.panel_z_voltage = self._io.read_u2be()
            self.panel_x_current = self._io.read_u2be()
            self.panel_y_current = self._io.read_u2be()
            self.panel_z_current = self._io.read_u2be()
            self.eps_boot_cause = self._io.read_u1()
            self.eps_battery_mode = self._io.read_u1()
            self.mppt_x_temp = self._io.read_s2be()
            self.mppt_y_temp = self._io.read_s2be()
            self.eps_board_temp = self._io.read_s2be()
            self.battery_pack1_temp = self._io.read_s2be()
            self.battery_pack2_temp = self._io.read_s2be()
            self.battery_pack3_temp = self._io.read_s2be()
            self.solar_current = self._io.read_u2be()
            self.system_current = self._io.read_u2be()
            self.battery_voltage = self._io.read_u2be()
            self.gps_current = self._io.read_u1()
            self.pad_0 = self._io.read_u1()
            self.eps_boot_count = self._io.read_u2be()
            self.trx_pa_temp = self._io.read_s2be()
            self.trx_total_tx_cnt = self._io.read_u4be()
            self.trx_total_rx_cnt = self._io.read_u4be()
            self.last_rssi = self._io.read_s2be()
            self.radio_boot_cnt = self._io.read_u2be()
            self.obc_temp_1 = self._io.read_s2be()
            self.obc_temp_2 = self._io.read_s2be()
            self.gyro_x = self._io.read_s2be()
            self.gyro_y = self._io.read_s2be()
            self.gyro_z = self._io.read_s2be()
            self.mag_x = self._io.read_s2be()
            self.mag_y = self._io.read_s2be()
            self.mag_z = self._io.read_s2be()
            self.px_solar_panel_temp = self._io.read_s2be()
            self.py_solar_panel_temp = self._io.read_s2be()
            self.nx_solar_panel_temp = self._io.read_s2be()
            self.ny_solar_panel_temp = self._io.read_s2be()
            self.pz_solar_panel_temp = self._io.read_s2be()
            self.nz_solar_panel_temp = self._io.read_s2be()
            self.px_sun_sensor_coarse = self._io.read_u2be()
            self.py_sun_sensor_coarse = self._io.read_u2be()
            self.pz_sun_sensor_coarse = self._io.read_u2be()
            self.nx_sun_sensor_coarse = self._io.read_u2be()
            self.ny_sun_sensor_coarse = self._io.read_u2be()
            self.nz_sun_sensor_coarse = self._io.read_u2be()
            self.eps_outputs_status = self._io.read_u1()
            self.pad_1 = self._io.read_u1()
            self.obc_boot_counter = self._io.read_s2be()
            self.leds_status = self._io.read_u1()
            self.pad_2 = self._io.read_u1()
            self.gps_status = self._io.read_u1()
            self.pad_3 = self._io.read_u1()
            self.gps_fix_time = self._io.read_u4be()
            self.gps_lat = self._io.read_s4be()
            self.gps_lon = self._io.read_s4be()
            self.gps_alt = self._io.read_s4be()
            self.software_status = self._io.read_u1()
            self.pad_4 = self._io.read_u1()
            self.ext_gyro_x = self._io.read_s2be()
            self.ext_gyro_y = self._io.read_s2be()
            self.ext_gyro_z = self._io.read_s2be()
            self.ext_mag_x = self._io.read_s2be()
            self.ext_mag_y = self._io.read_s2be()
            self.ext_mag_z = self._io.read_s2be()
            self.pad_5 = self._io.read_u2be()


    @property
    def framelength(self):
        if hasattr(self, '_m_framelength'):
            return self._m_framelength if hasattr(self, '_m_framelength') else None

        self._m_framelength = self._io.size()
        return self._m_framelength if hasattr(self, '_m_framelength') else None


