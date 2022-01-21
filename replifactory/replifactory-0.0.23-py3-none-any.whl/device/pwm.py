import time
import threading
import pyftdi.i2c


class PwmController:
    """PCA9685 PWM controller"""
    def __init__(self, device, frequency=50):
        self.device = device
        self.frequency = frequency
        self.lock = threading.Lock()  # valves and stirrers can be used on different threads
        self.port = None
        if self.device.is_connected():
            self.connect()

    def connect(self):
        try:
            self.port = self.device.i2c.get_port(self.device.PORT_PWM)
            self.set_frequency(self.frequency)
            for led_number in range(16):
                led_on_l = led_number * 4 + 6
                led_on_h = led_number * 4 + 7
                self.port.write_to(led_on_h, [0x0])
                self.port.write_to(led_on_l, [0x00])
            self.start_all()
        except pyftdi.i2c.I2cNackError:
            self.port = None
            print("PCA9685 PWM controller connection ERROR.")

    def set_frequency(self, frequency):
        pre_scale = round(25000000 / (4096 * frequency)) - 1
        try:
            self.port.write_to(0x00, [0b00010001])  # sleep mode
        except:
            time.sleep(0.5)
            self.port.write_to(0x00, [0b00010001])  # sleep mode
            self.port.write_to(0x00, [0b0])  # reset
            print("Reset PWM driver")
            self.port.write_to(0x00, [0b00010001])  # sleep mode
        self.port.write_to(0xFE, [pre_scale])  # SET_PWM_FREQUENCY
        self.port.write_to(0x00, [0b10000001])  # restart mode

    def get_duty_cycle(self, led_number):
        pass

    def set_duty_cycle(self, led_number, duty_cycle):
        assert 0 <= led_number <= 15
        assert 0 <= duty_cycle <= 1
        msb, lsb = divmod(round(4095 * duty_cycle), 0x100)  # most and least significant bytes
        led_off_l = led_number * 4 + 8
        led_off_h = led_number * 4 + 9
        self.port.write_to(led_off_l, [lsb])
        self.port.write_to(led_off_h, [msb])

    def stop_all(self):
        self.port.write_to(0x00, [0b10001])

    def start_all(self):
        self.port.write_to(0x00, [0b00001])
        time.sleep(0.002)
        self.port.write_to(0x00, [0b10000001])

    def is_sleeping(self):
        mode1_register = self.port.read_from(0x00, 1)[0]
        is_sleeping = bool(int(bin(mode1_register)[2:].rjust(8, '0')[-5]))  # sleep bit
        return is_sleeping
