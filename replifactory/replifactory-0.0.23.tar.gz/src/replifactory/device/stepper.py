import numpy as np


def split_bytes(value, n_bits, n_bytes):
    assert 0 <= value <= 1
    value = int(value*(2**n_bits-1))
    value = max(1, value)
    assert value < 2**n_bits

    bytes_list = [0b00]*n_bytes
    for i in range(n_bytes):
        lsb = value & ((1 << 8) - 1)
        value = value >> 8
        bytes_list[i] = lsb
    bytes_list = bytes_list[::-1]
    return bytes_list


class Stepper:
    REGISTER_ABS_POS = 0x01        # Current position, 22 bits
    REGISTER_EL_POS = 0x02         # Electrical position, 9 bits
    REGISTER_MARK = 0x03           # Mark position, 22 bits
    REGISTER_SPEED = 0x04          # Current speed, 20 bits
    REGISTER_ACC = 0x05            # Acceleration, 12 bits
    REGISTER_DEC = 0x06            # Deceleration, 12 bits
    REGISTER_MAX_SPEED = 0x07      # Maximum speed, 10 bits
    REGISTER_MIN_SPEED = 0x08      # Minimum speed, 13 bits
    REGISTER_FS_SPD = 0x15         # Full-step speed, 10 bits
    REGISTER_KVAL_HOLD = 0x09      # Holding KVAL, 8 bits
    REGISTER_KVAL_RUN = 0x0A       # Constant speed KVAL, 8 bits
    REGISTER_KVAL_ACC = 0x0B       # Acceleration starting KVAL, 8 bits
    REGISTER_KVAL_DEC = 0x0C       # Deceleration starting KVAL, 8 bits
    REGISTER_INT_SPEED = 0x0D      # Intersect speed, 14 bits
    REGISTER_ST_SLP = 0x0E         # Start slope, 8 bits
    REGISTER_FN_SLP_ACC = 0x0F     # Acceleration final slope, 8 bits
    REGISTER_FN_SLP_DEC = 0x10     # Deceleration final slope, 8 bits
    REGISTER_K_THERM = 0x11        # Thermal compensation factor, 4 bits
    REGISTER_ADC_OUT = 0x12        # ADC output, 5 bits
    REGISTER_OCD_TH = 0x13         # OCD threshold, 4 bits
    REGISTER_STALL_TH = 0x14       # STALL threshold, 7 bits
    REGISTER_STEP_MODE = 0x16      # Step mode, 8 bits
    REGISTER_ALARM_EN = 0x17       # Alarm enable, 8 bits
    REGISTER_CONFIG = 0x18         # IC configuration, 16 bits
    REGISTER_STATUS = 0x19         # Status, 16 bits

    min_speed_rps = 0.01
    max_speed_rps = 4
    acceleration = 0.01
    deceleration = 0.01
    full_step_speed = 0.1
    stall_threshold = 0.5
    _kval_hold = 0
    _kval_run = 0.8
    _kval_acc = 0.57
    _kval_dec = 0.3

    def __init__(self, device, cs):
        self.device = device
        self.cs = cs
        self.port = None
        self.step_mode = None
        if self.device.is_connected():
            self.connect()

    @property
    def kval_hold(self):
        return self._kval_hold

    @kval_hold.setter
    def kval_hold(self, value):
        assert 0 <= value <= 1
        self.write_register(self.REGISTER_KVAL_HOLD, value=value, n_bits=7, n_bytes=1)
        self._kval_hold=value

    @property
    def kval_acc(self):
        return self._kval_acc

    @kval_acc.setter
    def kval_acc(self, value):
        assert 0 <= value <= 1
        self.write_register(self.REGISTER_KVAL_ACC, value=value, n_bits=7, n_bytes=1)
        self._kval_acc = value


    @property
    def kval_dec(self):
        return self._kval_dec

    @kval_dec.setter
    def kval_dec(self, value):
        assert 0 <= value <= 1
        self.write_register(self.REGISTER_KVAL_DEC, value=value, n_bits=7, n_bytes=1)
        self._kval_dec = value

    @property
    def kval_run(self):
        return self._kval_run

    @kval_run.setter
    def kval_run(self, value):
        assert 0 <= value <= 1
        self.write_register(self.REGISTER_KVAL_RUN, value=value, n_bits=7, n_bytes=1)
        self._kval_run = value

    def connect(self):
        self.port = self.device.spi.get_port(cs=self.cs, freq=1e5, mode=3)
        # self.port.set_mode(3)
        self.write_register(self.REGISTER_FS_SPD, value=self.full_step_speed, n_bits=10, n_bytes=2)  # k value const
        self.write_register(self.REGISTER_STALL_TH, value=self.stall_threshold, n_bits=6, n_bytes=1)
        self.kval_hold=self._kval_hold
        self.kval_acc = self._kval_acc
        self.kval_run = self._kval_run
        # self.write_register(self.REGISTER_KVAL_HOLD, value=self.kval_hold, n_bits=7, n_bytes=1)
        # self.write_register(self.REGISTER_KVAL_RUN, value=self.kval_run, n_bits=7, n_bytes=1)
        # self.write_register(self.REGISTER_KVAL_ACC, value=self.kval_acc, n_bits=7, n_bytes=1)
        self.set_min_speed(rot_per_sec=self.min_speed_rps)
        self.set_max_speed(rot_per_sec=self.max_speed_rps)
        self.set_acceleration(value=self.acceleration)
        self.set_deceleration(value=self.deceleration)

    def set_acceleration(self, value=1e-4):
        self.write_register(self.REGISTER_ACC, value=value, n_bits=12, n_bytes=2)

    def set_deceleration(self, value=1e-3):
        self.write_register(self.REGISTER_DEC, value=value, n_bits=12, n_bytes=2)

    def set_min_speed(self, rot_per_sec=0.1):
        # steps_per_sec = integer * 2**-24/250e-9   # page 43 in L6470H datasheet
        correction_factor = 1.322
        rot_per_sec = rot_per_sec * correction_factor
        steps_per_sec = rot_per_sec * 2 ** 22 / 25600
        integer = steps_per_sec * 250e-9/2**-24
        self.write_register(self.REGISTER_MIN_SPEED, value=integer/2**12, n_bits=12, n_bytes=2)

    def set_max_speed(self, rot_per_sec=5.0):
        # steps_per_sec = integer * 2**-18/250e-9   # page 43 in L6470H datasheet
        correction_factor = 1.322
        rot_per_sec = rot_per_sec * correction_factor
        steps_per_sec = rot_per_sec * 2 ** 22 / 25600
        integer = steps_per_sec * 250e-9 / 2 ** -18
        self.write_register(self.REGISTER_MAX_SPEED, value=integer/2**10, n_bits=10, n_bytes=2)

    def write_register(self, reg, value, n_bits, n_bytes):
        set_param = reg | 0b00000000
        self.port.write([set_param])
        bytes_to_write = split_bytes(value, n_bits, n_bytes)
        for b in bytes_to_write:
            self.port.write([b])
        bytes_read = self.read_register(reg=reg, n_bytes=n_bytes)
        assert [bytes_to_write[i] == bytes_read[i] for i in range(n_bytes)]

    def read_register(self, reg, n_bytes=3):
        get_param = reg | 0b00100000
        self.port.write([get_param])
        res = []
        for b in range(n_bytes):
            res += self.port.read(1)
        return res

    def move(self, n_rotations=1):
        """
        move the given number of rotations
        By default uses 1/128 microstepping to minimize noise and vibration.
        If number of required microsteps can not fit in the register (> 2^22),
        the step mode is decreased to 1/64 or lower.
        """
        # if n_rotations <= 1:
        #     self.set_max_speed(rot_per_sec=0.1)
        # else:
        #     self.set_max_speed(rot_per_sec=self.max_speed_rps)

        if self.step_mode != 7:
            self.set_step_mode(7)
        assert not self.is_pumping()
        assert self.device.valves.not_all_closed()
        if n_rotations >= 0:
            direction_bit = 0b1
        else:
            direction_bit = 0b0

        move_header_byte = 0b01000000 | direction_bit
        max_n_microsteps = 2**22  # 22 bit

        steps_per_rotation = 200
        microsteps_per_step = 2 ** self.step_mode
        n_microsteps = abs(n_rotations) * steps_per_rotation * microsteps_per_step

        if n_microsteps > max_n_microsteps:
            required_step_mode = self.step_mode - 1 - int(np.log2(n_microsteps/max_n_microsteps))
            self.set_step_mode(required_step_mode)
            microsteps_per_step = 2 ** self.step_mode
            n_microsteps = abs(n_rotations) * steps_per_rotation * microsteps_per_step

        write_bytes = split_bytes(n_microsteps/max_n_microsteps, 22, 3)
        self.port.write([move_header_byte])
        for b in write_bytes:
            self.port.write([b])

    def run(self, speed=0.001):
        """
        run indefinitely at constant speed
        """
        if self.step_mode != 7:
            self.set_step_mode(7)

        if speed >= 0:
            direction_bit = 0b1
        else:
            direction_bit = 0b0
        speed = abs(speed)

        run_header_byte = 0b01010000 | direction_bit
        write_bytes = split_bytes(speed, 20, 3)
        self.port.write([run_header_byte])
        for b in write_bytes:
            self.port.write([b])

    def print_status(self):
        msb, lsb = self.read_register(self.REGISTER_STATUS, n_bytes=2)
        step_loss_a = not (msb >> 5 & 0b1)
        step_loss_b = not (msb >> 6 & 0b1)

        step_loss_string = ""
        if step_loss_a:
            step_loss_string += "stall on bridge a; "
        if step_loss_b:
            step_loss_string += "stall on bridge b; "
        if not (step_loss_b or step_loss_a):
            step_loss_string += "no step loss detected"

        overcurrent = not (msb >> 4 & 0b1)
        thermal_shutdown = not (msb >> 3 & 0b1)     # 160 deg C
        thermal_warning = not (msb >> 2 & 0b1)      # 130 deg C
        undervoltage_lockout = not (msb >> 1 & 0b1)
        status = lsb >> 5 & 0b11  # 00: stopped, 01:accelerating, 10:decelerating, 11:constant speed
        status_string = ["stopped", "accelerating", "decelerating", "moving at constant speed"][status]
        busy = not (lsb >> 1 & 0b1)
        high_impedance = bool(lsb & 0b1)
        print("Overcurrent:\t", overcurrent)
        print("Thermal shutdown:\t", thermal_shutdown)
        print("Thermal warning:\t", thermal_warning)
        print("Undervoltage lockout flag:\t", undervoltage_lockout)
        print("Status:\t", status_string)
        print("Busy:\t", busy)
        print("High impedance:\t", high_impedance)
        print("Step loss:\t", step_loss_string)
        self.port.write([0b11010000])  # GetStatus command, resets warning flags

    def is_busy(self):
        self.port.write([0b11010000])  # GetStatus command, resets warning flags
        msb, lsb = self.read_register(self.REGISTER_STATUS, n_bytes=2)
        busy = not (lsb >> 1 & 0b1)
        return busy

    def driver_is_responsive(self):
        self.port.write([0x19])  # GetStatus command, resets warning flags
        msb, lsb = self.read_register(self.REGISTER_STATUS, n_bytes=2)
        return not (msb == 255 and lsb == 255)

    def is_pumping(self):
        if not self.driver_is_responsive():
            return False
        self.port.write([0b11010000])  # GetStatus command, resets warning flags
        msb, lsb = self.read_register(self.REGISTER_STATUS, n_bytes=2)
        status = lsb >> 5 & 0b11
        return status > 0

    def is_hiz(self):
        msb, lsb = self.read_register(self.REGISTER_STATUS, n_bytes=2)
        hiz = bool(lsb & 0b1)
        return hiz

    def stop(self):
        """
        decelerate with programmed deceleration value until the MIN_SPEED value
        is reached and then stop the motor
        """
        self.port.write([0b10110000])

    def stop_hard(self):
        """
        stop the motor instantly, ignoring deceleration constraints
        """
        self.port.write([0b10111000])

    def hard_hiz(self):
        self.port.write([0b10101000])  # Hard HiZ

    def soft_hiz(self):
        self.port.write([0b10100000])  # soft HiZ

    def reset(self):
        self.port.write([0b11000000])
        self.__init__(device=self.device, cs=self.cs)

    def set_step_mode(self, mode=7):
        """
        See page 48 in L6470H datasheet

        0: Full-step
        1: Half-step
        2: 1/4 microstep
        3: 1/8 microstep
        4: 1/16 microstep
        5: 1/32 microstep
        6: 1/64 microstep
        7: 1/128 microstep
        """
        assert mode in [0, 1, 2, 3, 4, 5, 6, 7]
        assert not self.is_pumping()
        self.hard_hiz()
        self.port.write([self.REGISTER_STEP_MODE])
        self.port.write([mode])
        read_mode = self.read_register(self.REGISTER_STEP_MODE)[0]
        assert mode == read_mode
        self.step_mode = mode
