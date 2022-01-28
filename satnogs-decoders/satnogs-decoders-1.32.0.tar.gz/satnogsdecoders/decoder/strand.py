# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Strand(KaitaiStruct):
    """:field seq_no: seq_no
    :field length: length
    :field packet_type: packet_type
    :field channel: body.channel
    :field time_since_last_obc_i2c_message: body.data.time_since_last_obc_i2c_message
    :field packets_up_count: body.data.packets_up_count
    :field packets_down_count: body.data.packets_down_count
    :field packets_up_dropped_count: body.data.packets_up_dropped_count
    :field packets_down_dropped_count: body.data.packets_down_dropped_count
    :field i2c_node_address: body.i2c_node_address
    :field i2c_node_address: body.node.i2c_node_address
    :field battery_0_current_direction: body.node.node.battery_0_current_direction
    :field battery_0_current_ma: body.node.node.battery_0_current_ma
    :field battery_0_voltage_v: body.node.node.battery_0_voltage_v
    :field battery_0_temperature_deg_c: body.node.node.battery_0_temperature_deg_c
    :field battery_1_current_direction: body.node.node.battery_1_current_direction
    :field battery_1_current_ma: body.node.node.battery_1_current_ma
    :field battery_1_voltage_v: body.node.node.battery_1_voltage_v
    :field battery_1_temperature_deg_c: body.node.node.battery_1_temperature_deg_c
    :field adc1_py_array_current: body.node.node.adc1_py_array_current
    :field adc2_py_array_temperature: body.node.node.adc2_py_array_temperature
    :field adc3_array_pair_y_voltage: body.node.node.adc3_array_pair_y_voltage
    :field adc4_my_array_current: body.node.node.adc4_my_array_current
    :field adc5_my_array_temperature: body.node.node.adc5_my_array_temperature
    :field adc6_array_pair_x_voltage: body.node.node.adc6_array_pair_x_voltage
    :field adc7_mx_array_current: body.node.node.adc7_mx_array_current
    :field adc8_mx_array_temperature: body.node.node.adc8_mx_array_temperature
    :field adc9_array_pair_z_voltage: body.node.node.adc9_array_pair_z_voltage
    :field adc10_pz_array_current: body.node.node.adc10_pz_array_current
    :field adc11_pz_array_temperature: body.node.node.adc11_pz_array_temperature
    :field adc13_px_array_current: body.node.node.adc13_px_array_current
    :field adc14_px_array_temperature: body.node.node.adc14_px_array_temperature
    :field adc17_battery_bus_current: body.node.node.adc17_battery_bus_current
    :field adc26_5v_bus_current: body.node.node.adc26_5v_bus_current
    :field adc27_33v_bus_current: body.node.node.adc27_33v_bus_current
    :field adc30_mz_array_temperature: body.node.node.adc30_mz_array_temperature
    :field adc31_mz_array_current: body.node.node.adc31_mz_array_current
    :field switch_0_ppt_power_supply_status: body.node.node.switch_0_ppt_power_supply_status
    :field switch_1_ppt_1_2_status: body.node.node.switch_1_ppt_1_2_status
    :field switch_2_phone_5v_webcam: body.node.node.switch_2_phone_5v_webcam
    :field switch_3_warp_valve_status: body.node.node.switch_3_warp_valve_status
    :field switch_4_warp_heater_status: body.node.node.switch_4_warp_heater_status
    :field switch_5_digi_wi9c_status: body.node.node.switch_5_digi_wi9c_status
    :field switch_6_sgr05_status: body.node.node.switch_6_sgr05_status
    :field switch_7_reaction_wheels: body.node.node.switch_7_reaction_wheels
    :field switch_8_solar_panel_deploy_arm: body.node.node.switch_8_solar_panel_deploy_arm
    :field switch_9_solar_panel_deploy_fire: body.node.node.switch_9_solar_panel_deploy_fire
    :field unix_time_little_endian: body.node.node.unix_time_little_endian
    :field magnetometer_set_1: body.node.node.magnetometer_set_1
    :field magnetometer_set_2: body.node.node.magnetometer_set_2
    
    .. seealso::
       Source - https://ukamsat.files.wordpress.com/2013/03/amsat-strand-1-20130327.xlsx
       https://amsat-uk.org/satellites/telemetry/strand-1/strand-1-telemetry/
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.hdlc_flag = self._io.read_bytes(2)
        if not self.hdlc_flag == b"\xC0\x80":
            raise kaitaistruct.ValidationNotEqualError(b"\xC0\x80", self.hdlc_flag, self._io, u"/seq/0")
        self.seq_no = self._io.read_u1()
        self.length = self._io.read_u1()
        self.packet_type = self._io.read_u1()
        _on = self.packet_type
        if _on == 1:
            self.body = Strand.ModemBeaconTlm(self._io, self, self._root)
        elif _on == 2:
            self.body = Strand.ObcBeaconTlm(self._io, self, self._root)
        self.crc_16_ccit = self._io.read_bytes(2)

    class ChAdc1PyArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc1_py_array_current = self._io.read_u1()


    class ChSwitch1Ppt12Status(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_1_ppt_1_2_status = self._io.read_u1()


    class ChAdc9ArrayPairZVoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc9_array_pair_z_voltage = self._io.read_u1()


    class ChBattery1CurrentDirection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_current_direction = self._io.read_u1()


    class ModemBeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.channel = self._io.read_u1()
            _on = self.channel
            if _on == 224:
                self.data = Strand.ChTimeSinceLastObcI2cMessage(self._io, self, self._root)
            elif _on == 227:
                self.data = Strand.ChPacketsUpDroppedCount(self._io, self, self._root)
            elif _on == 226:
                self.data = Strand.ChPacketsDownCount(self._io, self, self._root)
            elif _on == 225:
                self.data = Strand.ChPacketsUpCount(self._io, self, self._root)
            elif _on == 228:
                self.data = Strand.ChPacketsDownDroppedCount(self._io, self, self._root)


    class ChMagnetometerSet1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magnetometer_set_1 = self._io.read_u1()


    class CsBattery(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 14:
                self.node = Strand.ChAdc14PxArrayTemperature(self._io, self, self._root)
            elif _on == 10:
                self.node = Strand.ChAdc10PzArrayCurrent(self._io, self, self._root)
            elif _on == 17:
                self.node = Strand.ChAdc17BatteryBusCurrent(self._io, self, self._root)
            elif _on == 4:
                self.node = Strand.ChAdc4MyArrayCurrent(self._io, self, self._root)
            elif _on == 6:
                self.node = Strand.ChAdc6ArrayPairXVoltage(self._io, self, self._root)
            elif _on == 7:
                self.node = Strand.ChAdc7MxArrayCurrent(self._io, self, self._root)
            elif _on == 1:
                self.node = Strand.ChAdc1PyArrayCurrent(self._io, self, self._root)
            elif _on == 27:
                self.node = Strand.ChAdc2733vBusCurrent(self._io, self, self._root)
            elif _on == 13:
                self.node = Strand.ChAdc13PxArrayCurrent(self._io, self, self._root)
            elif _on == 11:
                self.node = Strand.ChAdc11PzArrayTemperature(self._io, self, self._root)
            elif _on == 3:
                self.node = Strand.ChAdc3ArrayPairYVoltage(self._io, self, self._root)
            elif _on == 5:
                self.node = Strand.ChAdc5MyArrayTemperature(self._io, self, self._root)
            elif _on == 8:
                self.node = Strand.ChAdc8MxArrayTemperature(self._io, self, self._root)
            elif _on == 9:
                self.node = Strand.ChAdc9ArrayPairZVoltage(self._io, self, self._root)
            elif _on == 26:
                self.node = Strand.ChAdc265vBusCurrent(self._io, self, self._root)
            elif _on == 31:
                self.node = Strand.ChAdc31MzArrayCurrent(self._io, self, self._root)
            elif _on == 2:
                self.node = Strand.ChAdc2PyArrayTemperature(self._io, self, self._root)
            elif _on == 30:
                self.node = Strand.ChAdc30MzArrayTemperature(self._io, self, self._root)


    class ChAdc3ArrayPairYVoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc3_array_pair_y_voltage = self._io.read_u1()


    class ChSwitch9SolarPanelDeployFire(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_9_solar_panel_deploy_fire = self._io.read_u1()


    class ChBattery1VoltageV(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_voltage_v = self._io.read_u1()


    class ChAdc4MyArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc4_my_array_current = self._io.read_u1()


    class ChAdc2PyArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc2_py_array_temperature = self._io.read_u1()


    class ChUnixTimeLittleEndian(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unix_time_little_endian = self._io.read_u1()


    class ChTimeSinceLastObcI2cMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_since_last_obc_i2c_message = self._io.read_u1()


    class ChSwitch0PptPowerSupplyStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_0_ppt_power_supply_status = self._io.read_u1()


    class ChBattery0CurrentDirection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_current_direction = self._io.read_u1()


    class ObcData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 12:
                self.node = Strand.ChUnixTimeLittleEndian(self._io, self, self._root)


    class ChMagnetometerSet2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magnetometer_set_2 = self._io.read_u1()


    class ChAdc2733vBusCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc27_33v_bus_current = self._io.read_u1()


    class ChSwitch6Sgr05Status(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_6_sgr05_status = self._io.read_u1()


    class CsEps(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 0:
                self.node = Strand.ChBattery0CurrentDirection(self._io, self, self._root)
            elif _on == 4:
                self.node = Strand.ChBattery0TemperatureDegC(self._io, self, self._root)
            elif _on == 6:
                self.node = Strand.ChBattery1CurrentMa(self._io, self, self._root)
            elif _on == 1:
                self.node = Strand.ChBattery0CurrentMa(self._io, self, self._root)
            elif _on == 3:
                self.node = Strand.ChBattery0VoltageV(self._io, self, self._root)
            elif _on == 5:
                self.node = Strand.ChBattery1CurrentDirection(self._io, self, self._root)
            elif _on == 8:
                self.node = Strand.ChBattery1VoltageV(self._io, self, self._root)
            elif _on == 9:
                self.node = Strand.ChBattery1TemperatureDegC(self._io, self, self._root)


    class ChAdc7MxArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc7_mx_array_current = self._io.read_u1()


    class ChAdc31MzArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc31_mz_array_current = self._io.read_u1()


    class ChSwitch8SolarPanelDeployArm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_8_solar_panel_deploy_arm = self._io.read_u1()


    class ChAdc5MyArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc5_my_array_temperature = self._io.read_u1()


    class ChPacketsDownDroppedCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_down_dropped_count = self._io.read_u1()


    class ObcBeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 45:
                self.node = Strand.CsBattery(self._io, self, self._root)
            elif _on == 137:
                self.node = Strand.Magnetometers(self._io, self, self._root)
            elif _on == 44:
                self.node = Strand.CsEps(self._io, self, self._root)
            elif _on == 102:
                self.node = Strand.SwitchBoard(self._io, self, self._root)
            elif _on == 128:
                self.node = Strand.ObcData(self._io, self, self._root)


    class ChPacketsUpCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_up_count = self._io.read_u1()


    class ChSwitch3WarpValveStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_3_warp_valve_status = self._io.read_u1()


    class ChBattery0VoltageV(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_voltage_v = self._io.read_u1()


    class ChAdc13PxArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc13_px_array_current = self._io.read_u1()


    class ChAdc30MzArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc30_mz_array_temperature = self._io.read_u1()


    class ChAdc8MxArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc8_mx_array_temperature = self._io.read_u1()


    class ChAdc14PxArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc14_px_array_temperature = self._io.read_u1()


    class ChBattery0CurrentMa(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_current_ma = self._io.read_u1()


    class ChAdc6ArrayPairXVoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc6_array_pair_x_voltage = self._io.read_u1()


    class ChSwitch2Phone5vWebcam(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_2_phone_5v_webcam = self._io.read_u1()


    class ChPacketsDownCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_down_count = self._io.read_u1()


    class ChAdc10PzArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc10_pz_array_current = self._io.read_u1()


    class ChAdc17BatteryBusCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc17_battery_bus_current = self._io.read_u1()


    class ChAdc11PzArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc11_pz_array_temperature = self._io.read_u1()


    class ChSwitch4WarpHeaterStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_4_warp_heater_status = self._io.read_u1()


    class ChPacketsUpDroppedCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_up_dropped_count = self._io.read_u1()


    class ChSwitch7ReactionWheels(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_7_reaction_wheels = self._io.read_u1()


    class ChBattery1TemperatureDegC(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_temperature_deg_c = self._io.read_u1()


    class ChSwitch5DigiWi9cStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_5_digi_wi9c_status = self._io.read_u1()


    class SwitchBoard(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 159:
                self.node = Strand.ChSwitch6Sgr05Status(self._io, self, self._root)
            elif _on == 169:
                self.node = Strand.ChSwitch8SolarPanelDeployArm(self._io, self, self._root)
            elif _on == 144:
                self.node = Strand.ChSwitch3WarpValveStatus(self._io, self, self._root)
            elif _on == 149:
                self.node = Strand.ChSwitch4WarpHeaterStatus(self._io, self, self._root)
            elif _on == 172:
                self.node = Strand.ChSwitch9SolarPanelDeployFire(self._io, self, self._root)
            elif _on == 164:
                self.node = Strand.ChSwitch7ReactionWheels(self._io, self, self._root)
            elif _on == 129:
                self.node = Strand.ChSwitch0PptPowerSupplyStatus(self._io, self, self._root)
            elif _on == 134:
                self.node = Strand.ChSwitch1Ppt12Status(self._io, self, self._root)
            elif _on == 139:
                self.node = Strand.ChSwitch2Phone5vWebcam(self._io, self, self._root)
            elif _on == 154:
                self.node = Strand.ChSwitch5DigiWi9cStatus(self._io, self, self._root)


    class ChBattery0TemperatureDegC(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_temperature_deg_c = self._io.read_u1()


    class ChAdc265vBusCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc26_5v_bus_current = self._io.read_u1()


    class Magnetometers(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 3:
                self.node = Strand.ChMagnetometerSet1(self._io, self, self._root)
            elif _on == 5:
                self.node = Strand.ChMagnetometerSet2(self._io, self, self._root)


    class ChBattery1CurrentMa(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_current_ma = self._io.read_u1()



