import time
import pyftdi.i2c
from pyftdi.spi import SpiController
import threading
import os
import yaml
from matplotlib import pyplot as plt

from replifactory.device.adc import Photodiodes
from replifactory.device.lasers import Lasers
from replifactory.device.od_sensor import OdSensor, measure_od_all
from replifactory.device.pwm import PwmController
from replifactory.device.stirrers import Stirrers
from replifactory.device.pump import Pump, calibrate_pump
from replifactory.device.thermometers import Thermometers
from replifactory.device.valves import Valves
from replifactory.device.dilution import make_dilution
from replifactory.util import CultureDict
from replifactory.loading import save_object, load_config, load_object
from replifactory.device.workers import QueueWorker


class BaseDevice:
    PORT_ADC = 0x68  # MCP3421A0  1101 000
    # PORT_ADC = 0x69  # MCP3421A1  1101 001
    # PORT_ADC = 0x6a  # MCP3421A2  1101 010
    # PORT_ADC = 0x6b  # MCP3421A3  1101 011
    PORT_GPIO_MULTIPLEXER_LASERS = 0x20  # PCA 9555
    PORT_GPIO_MULTIPLEXER_ADC = 0x21  # PCA 9555
    PORT_GPIO_MULTIPLEXER_STIRRERS = 0x25  # PCA 9555
    PORT_THERMOMETER_VIALS = 0x49  # ADT 75  #0x4C?
    PORT_THERMOMETER_BOARD = 0x48  # ADT 75
    PORT_PWM = 0x70  # PCA9685

    def __init__(self, ftdi_address='ftdi://ftdi:2232h', connect=False):
        self.ftdi_address = ftdi_address
        self.directory = None
        self.cultures = CultureDict(self)
        self.cultures[1] = None
        self.cultures[2] = None
        self.cultures[3] = None
        self.cultures[4] = None
        self.cultures[5] = None
        self.cultures[6] = None
        self.cultures[7] = None

        self.dilution_worker = None
        self.od_worker = None

        self.hard_stop_trigger = False
        self.soft_stop_trigger = False

        self.i2c = None
        self.spi = None

        self.calibration_od_to_mv = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}
        self.calibration_fan_speed_to_duty_cycle = {1: {1: None, 2: None, 3: None},
                                                    2: {1: None, 2: None, 3: None},
                                                    3: {1: None, 2: None, 3: None},
                                                    4: {1: None, 2: None, 3: None},
                                                    5: {1: None, 2: None, 3: None},
                                                    6: {1: None, 2: None, 3: None},
                                                    7: {1: None, 2: None, 3: None}}
        self.calibration_pump_rotations_to_ml = {1: {},
                                                 2: {},
                                                 3: {},
                                                 4: {}}

        self.delay_tube_wash_hrs = 24
        self.pump1_flush_volume = 1
        self.pump2_flush_volume = 0.1
        self.pump3_flush_volume = 0

        self.locks_vials = {v: threading.Lock() for v in range(1, 8)}
        self.lock_pumps = threading.Lock()
        self.file_lock = threading.Lock()

        # self.pump_calibrations_rotations_to_ml = {1: {}, 2: {}, 3: {}, 4: {}}
        self.pump_stock_concentrations = {1: None, 2: None, 3: None, 4: None}
        self.pump_stock_volumes = {1: None, 2: None, 3: None, 4: None}

        self.od_values = {v: None for v in range(1, 8)}
        self.pwm_controller = PwmController(device=self, frequency=50)
        self.valves = Valves(device=self)
        self.stirrers = Stirrers(device=self)
        self.photodiodes = Photodiodes(device=self)
        self.lasers = Lasers(device=self)
        self.od_sensors = {v: OdSensor(device=self, vial_number=v) for v in range(1, 8)}
        self.pump1 = Pump(device=self, cs=0)
        self.pump2 = Pump(device=self, cs=1)
        self.pump3 = Pump(device=self, cs=2)
        self.pump4 = Pump(device=self, cs=3)
        self.thermometers = Thermometers(device=self)
        # if self.ftdi_address is not None:
        #     self.connect()
        if self.directory is not None:
            try:
                self.load()
            except FileNotFoundError:
                self.save()
        if connect:
            self.connect()

    def connect(self, ftdi_address='ftdi://ftdi:2232h', fit_calibration=False):
        # if ftdi_address is None:
        #     ftdi_address = self.ftdi_address
        # else:
        try:
            self.spi = SpiController(cs_count=4)
            self.spi.configure(ftdi_address + '/1')
            self.i2c = pyftdi.i2c.I2cController()
            self.i2c.configure(ftdi_address + '/2', frequency=5e4)
            self.pwm_controller.connect()
            self.valves.connect()
            self.stirrers.connect()
            self.photodiodes.connect()
            self.lasers.connect()
            self.thermometers.connect()
            self.pump1.connect()
            self.pump2.connect()
            self.pump3.connect()
            self.pump4.connect()
            print("Device %s connection established" % ftdi_address)
            self.dilution_worker = QueueWorker(device=self, worker_name="dilution")
            self.od_worker = QueueWorker(device=self, worker_name="od")
            if self.directory is not None and fit_calibration:
                try:
                    self.fit_calibration_functions()
                    self.check_parameters()
                except:
                    print("Calibration incomplete")
                self.save()
        except pyftdi.ftdi.FtdiError:
            print("%s \nwith address %s is not connected!" % (str(self.__class__), ftdi_address))
        except pyftdi.usbtools.USBError:
            print("Device connected but does not recognize the command.\nPlease reset connections.")
        except pyftdi.usbtools.UsbToolsError:
            print("Device %s not connected." % ftdi_address)
        for lock in self.locks_vials.values():
            if lock.locked():
                lock.release()

    def pump_to(self, vial, p1=0, p2=0, p3=0, p4=0):
        if self.valves.not_all_closed():
            self.valves.close_all()
        self.valves.open(vial)  # valve number might be different for e.g. a lagoon setup
        if p1 > 0:
            self.pump1.pump(p1)
        if p2 > 0:
            self.pump2.pump(p2)
        if p3 > 0:
            self.pump3.pump(p3)
        if p4 > 0:
            self.pump4.pump(p4)
        while self.is_pumping():
            time.sleep(0.5)
        time.sleep(0.5)
        self.valves.close(vial)  # valve number might be different for e.g. a lagoon setup

    def update_cultures(self):
        def queued_function():
            for v, c in self.cultures.items():
                if self.soft_stop_trigger:
                    break
                if c is not None:
                    c.update()

        if self.dilution_worker.queue.empty():
            self.dilution_worker.queue.put(queued_function)
        else:
            print("Culture update not queued. dilution thread queue is not empty.")

    @property
    def pumps(self):
        return {1: self.pump1,
                2: self.pump2,
                3: self.pump3,
                4: self.pump4}

    def make_dilution(self, vial, pump1_volume=0, pump2_volume=0, pump3_volume=0, extra_vacuum=5):
        make_dilution(device=self, vial=vial, pump1_volume=pump1_volume, pump2_volume=pump2_volume,
                      pump3_volume=pump3_volume, extra_vacuum=extra_vacuum)

    def measure_od_all(self):
        vials_to_measure = []
        for v in self.cultures.keys():
            culture = self.cultures[v]
            if culture is not None:
                vials_to_measure += [v]

        def queued_function():
            measure_od_all(device=self, vials_to_measure=vials_to_measure)
        if self.od_worker.queue.empty():
            self.od_worker.queue.put(queued_function)
        else:
            print("OD measurement not queued. od thread queue is not empty.")

    def measure_temperature(self):
        def queued_function():
            self.thermometers.measure_temperature()
        if self.od_worker.queue.empty():
            self.od_worker.queue.put(queued_function)
        else:
            print("Temperature measurement not queued. od thread queue is not empty.")

    def prime_tubing(self, vial_number, pump_number, volume):
        self.lock_pumps.acquire()
        self.locks_vials[vial_number].acquire()
        self.valves.open(valve=vial_number)
        for i in range(20):
            q = input("%.2f ml of air available in pump_number %d tubing to vial %d?" % (volume,pump_number,vial_number))
            if q == "":
                self.pumps[pump_number].pump(volume=volume)
                while self.is_pumping():
                    time.sleep(0.5)
            else:
                break
        self.valves.close(valve=vial_number)
        self.lock_pumps.release()
        self.locks_vials[vial_number].release()

    def flush_tubing(self):
        """
        to prevent tube drying
        """
        def queued_function():
            for v in range(1, 8):
                c = self.cultures[v]
                if c is not None:
                    c.flush_tubing_if_necessary()
        self.dilution_worker.queue.put(queued_function)

    def is_pumping(self):
        return any(p.is_pumping() for p in [self.pump1, self.pump2, self.pump3, self.pump4])

    def emergency_stop(self):
        self.hard_stop_trigger = True
        self.pump1.stop()
        self.pump2.stop()
        self.pump3.stop()
        self.pump4.stop()
        self.pwm_controller.stop_all()

    def is_connected(self):
        """
        tries to send spi command. If device does not respond, returns False.
        """
        try:
            self.pump1.is_busy()
            return True
        except:
            return False

    def save(self):
        """
        saves calibration data and stock concentrations to self.directory/device_config.yaml
        """
        config_path = os.path.join(self.directory, "device_config.yaml")
        save_object(self, filepath=config_path)

    def load(self):
        self.file_lock.acquire()
        config_path = os.path.join(self.directory, "device_config.yaml")
        load_config(self, filepath=config_path)
        self.file_lock.release()
        print("Loaded device config.")
        for v in range(1, 8):
            vial_directory = os.path.join(self.directory, "vial_%d" % v)
            vial_config_path = os.path.join(vial_directory, "culture_config.yaml")
            self.cultures[v] = load_object(vial_config_path)
        print()

    def calibrate(self, dummy_data=False):
        if dummy_data:
            # self.calibration_mv_to_od = {1: {1: 5, 10: 2, 22: 0.5, 35: 0.1, 41: 0.0001},
            #                              2: {1: 5, 10: 2, 22: 0.5, 35: 0.1, 41: 0.0001},
            #                              3: {1: 5, 10: 2, 35: 0.1, 41: 0.0001},
            #                              4: {1: 5, 10: 2, 35: 0.1, 41: 0.0001},
            #                              5: {1: 5, 10: 2, 35: 0.1, 41: 0.0001},
            #                              6: {1: 5, 10: 2, 35: 0.1, 41: 0.0001},
            #                              7: {1: 5, 10: 2, 35: 0.1, 41: 0.0001}}
            for v in range(1,8):
                self.calibration_od_to_mv[v] = {11.973: [0.40625, 0.4103125],
                                                 5.644: [0.75, 0.7575],
                                                 2.661: [1.6484375, 1.664921875],
                                                 1.254: [4.2890625, 4.331953125],
                                                 0.591: [10.6796875, 10.786484375],
                                                 0.279: [21.1015625, 21.312578125],
                                                 0.131: [29.8671875, 30.165859375],
                                                 0.062: [38.1328125, 38.514140625],
                                                 0.029: [42.515625, 42.94078125],
                                                 0.014: [45.71875, 46.1759375],
                                                 0: [47.859375, 48.33796875]}

            self.calibration_fan_speed_to_duty_cycle = {1: {1: 0.3, 2: 0.6, 3: 1},
                                                        2: {1: 0.3, 2: 0.6, 3: 1},
                                                        3: {1: 0.3, 2: 0.6, 3: 1},
                                                        4: {1: 0.3, 2: 0.6, 3: 1},
                                                        5: {1: 0.3, 2: 0.6, 3: 1},
                                                        6: {1: 0.3, 2: 0.6, 3: 1},
                                                        7: {1: 0.3, 2: 0.6, 3: 1}}
            self.calibration_pump_rotations_to_ml = {1: {1: 0.184, 3: 0.55, 20: 3.59, 80: 14.23},
                                                     2: {1: 0.184, 3: 0.55, 20: 3.59, 80: 14.23},
                                                     3: {},
                                                     4: {1: 0.17, 5: 0.64, 10: 1.05, 50: 5.1, 100: 7.55, 200: 13.71}}
            self.save()
            self.fit_calibration_functions()

    def show_parameters(self):
        self.stirrers.show_parameters()
        print()
        self.pump1.show_parameters()
        self.pump2.show_parameters()
        self.pump3.show_parameters()
        self.pump4.show_parameters()
        print()
        for od_sensor in self.od_sensors.values():
            od_sensor.calibration_curve()
            plt.show()

    def load_calibration(self, config_path):
        assert config_path.endswith("device_config.yaml")
        config = open(config_path).read()
        loaded_dict = yaml.load(config, Loader=yaml.Loader)
        # assert loaded_dict["_class"] == self.__class__
        for k in loaded_dict.keys():
            if k != "directory":
                self.__dict__[k] = loaded_dict[k]
        print("Loaded calibration data from %s" % config_path)
        self.fit_calibration_functions()


    def copy_calibration(self, config_path):
        self.load_calibration(config_path=config_path)
        # self.check_parameters()
        self.save()

    def calibrate_pump(self, pump_number):
        calibrate_pump(device=self, pump_number=pump_number)

    def fill_vials(self, volume=15, vials=(1, 2, 3, 4, 5, 6, 7)):
        for v in vials:
            assert 1 <= v <= 7
        for v in vials:
            self.locks_vials[v].acquire()
            self.lock_pumps.acquire()
            self.valves.open(v)
            self.pump1.pump(volume)
            while self.is_pumping():
                time.sleep(0.5)
            time.sleep(2)
            assert not self.is_pumping()
            self.valves.close(v)
            self.locks_vials[v].release()
            self.lock_pumps.release()

    def aspirate_vials(self, volume=24, vials=(1, 2, 3, 4, 5, 6, 7)):
        for v in vials:
            assert 1 <= v <= 7
        for v in vials:
            self.locks_vials[v].acquire()
            self.lock_pumps.acquire()
            self.valves.open(v)
            self.pump4.pump(volume)
            while self.is_pumping():
                time.sleep(0.5)
            time.sleep(2)
            assert not self.is_pumping()
            self.valves.close(v)
            self.locks_vials[v].release()
            self.lock_pumps.release()

    def check_all(self):
        assert not self.hard_stop_trigger
        assert not self.soft_stop_trigger
        # if not self.is_connected():
        #     self.connect()
        if not self.is_connected():
            print("Device not connected.")
        assert not self.file_lock.locked()
        assert not self.lock_pumps.locked()
        for lock in self.locks_vials.values():
            assert not lock.locked()
        assert not self.is_pumping()
        self.check_parameters()
        self.check_cultures()

    def check_parameters(self):
        if self.pump1.stock_volume is None:
            print("Pump1 stock volume unknown.")
        if self.pump2.stock_volume is None:
            print("Pump2 stock volume unknown.")
        if self.pump2.stock_concentration is None:
            print("Pump2 stock concentration unknown.")
        if self.pump3.stock_volume is None:
            print("Pump3 stock volume unknown.")
        if self.pump4.stock_volume is None:
            print("Free waste bottle volume unknown.")

        for v in self.cultures.keys():
            if not callable(self.od_sensors[v].calibration_function):
                print("Vial %d OD calibration function missing." % v)
        if not callable(self.pump1.calibration_function):
            print("Pump 1 calibration function missing")
        if not callable(self.pump2.calibration_function):
            print("Pump 2 calibration function missing")
        # if not callable(self.pump3.calibration_function):
        #     print("Pump 3 calibration function missing")
        if not callable(self.pump4.calibration_function):
            print("Pump 4 calibration function missing")
        print("Calibration testing complete")

    def check_cultures(self):
        for v in self.cultures.keys():
            if self.cultures[v] is not None:
                self.cultures[v].check()

    def fit_calibration_functions(self):
        for v in range(1, 8):
            self.od_sensors[v].fit_calibration_function()
        self.pump1.fit_calibration_function()
        self.pump2.fit_calibration_function()
        self.pump3.fit_calibration_function()
        self.pump4.fit_calibration_function()
