import time


class Valves:
    VALVE_OPEN_TIME = 1.5
    VALVE_CLOSE_TIME = 1.5
    open_duty_cycle = 0.03
    closed_duty_cycle = 0.12
    led_numbers = {valve: valve+7 for valve in [1, 2, 3, 4, 5, 6, 7, 8]}

    def __init__(self, device):
        self.device = device
        self.pwm_controller = device.pwm_controller
        self.is_open = {1: None,
                        2: None,
                        3: None,
                        4: None,
                        5: None,
                        6: None,
                        7: None}

        if self.device.is_connected():
            self.connect()

    def not_all_closed(self):
        return any(v is True for v in self.is_open.values())
        # for v in self.is_open.values():
        #     if v is True:
        #         return True
        # return False

    def connect(self):
        if self.pwm_controller.port is not None:
            self.idle_all()

    # def set_duty_cycle_all(self, duty_cycle):
    #     self.pwm_controller.lock.acquire()
    #     try:
    #         self.pwm_controller.stop_all()
    #         for valve in range(1, 9):
    #             led_number = self.led_numbers[valve]
    #             self.pwm_controller.set_duty_cycle(led_number=led_number, duty_cycle=duty_cycle)
    #             time.sleep(0.5)
    #         self.pwm_controller.start_all()
    #     finally:
    #         self.pwm_controller.lock.release()

    def idle_all(self):
        """
        sets 0 duty cycle for all valves fast
        :return:
        """
        self.pwm_controller.lock.acquire()
        try:
            self.pwm_controller.stop_all()
            for valve in range(1, 9):
                led_number = self.led_numbers[valve]
                self.pwm_controller.set_duty_cycle(led_number=led_number, duty_cycle=0)
            self.pwm_controller.start_all()
        finally:
            self.pwm_controller.lock.release()

    def set_duty_cycle(self, valve, duty_cycle):
        """
        sets the duty cycle of the pwm signal for the valve.
        Stops pwm controller while changing value, to prevent the motor from
        moving after writing the first byte.
        """
        led_number = self.led_numbers[valve]
        self.pwm_controller.lock.acquire()
        try:
            # self.pwm_controller.stop_all()
            self.pwm_controller.set_duty_cycle(led_number=led_number, duty_cycle=duty_cycle)
            # self.pwm_controller.start_all()
            time.sleep(0.04)
        finally:
            self.pwm_controller.lock.release()

    def open(self, valve):
        self.set_duty_cycle(valve=valve, duty_cycle=self.open_duty_cycle)
        time.sleep(self.VALVE_OPEN_TIME)
        # self.pwm_controller.stop_all()
        # self.set_duty_cycle(valve=valve, duty_cycle=0)
        # self.pwm_controller.start_all()
        self.is_open[valve] = True

    def close(self, valve):
        self.set_duty_cycle(valve=valve, duty_cycle=self.closed_duty_cycle)
        time.sleep(self.VALVE_CLOSE_TIME)
        # self.pwm_controller.stop_all()
        # self.set_duty_cycle(valve=valve, duty_cycle=0)
        # self.pwm_controller.start_all()

        self.is_open[valve] = False

    def open_all(self):
        for valve in range(1, 8):
            if not self.is_open[valve]:
                self.open(valve=valve)

        # self.set_duty_cycle_all(duty_cycle=self.open_duty_cycle)
        # time.sleep(1)  # wait for valves to move
        # self.set_duty_cycle_all(duty_cycle=0)

    def close_all(self):
        assert not self.device.is_pumping()
        for valve in range(1, 8):
            if self.is_open[valve] in [True, None]:
                self.close(valve=valve)

        # self.set_duty_cycle_all(duty_cycle=self.closed_duty_cycle)
        # time.sleep(1)  # wait for valves to move
        # self.set_duty_cycle_all(duty_cycle=0)

    def set_state(self, valve, is_open=False):
        assert is_open in [True, False]
        if is_open:
            self.open(valve)
        else:
            self.close(valve)
