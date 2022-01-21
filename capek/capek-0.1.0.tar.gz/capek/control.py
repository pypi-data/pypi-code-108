from .protocol import Protocol


class Control:
    def __init__(self, accel: float = 0, brake: float = 0, clutch: float = 0,
                 gear: int = 1, steering: float = 0, focus: float = 0, meta: int = 0):
        """
        Class representing the available effectors.

        Parameters:
            accel (float)    Virtual gas pedal (0 means no gas, 1 full gas).
            brake (float)    Virtual brake pedal (0 means no brake, 1 full brake).
            clutch (float)   Virtual clutch pedal (0 means no clutch, 1 full clutch).
            gear (int)       Gear value.
            steering (float) -1 and +1 means respectively full right and left, corresponds to an angle of 0.366519 rad.
            focus (float)    Focus direction in degrees.
            meta (int)       Meta-control command: 0 do nothing, 1 ask competition server to restart the race.
        """
        self._accel = accel
        self._brake = brake
        self._clutch = clutch
        self._gear = gear
        self._steering = steering
        self._focus = focus
        self._meta = meta

    def __str__(self) -> str:
        """
        Encode control information with TORCS SCR protocol.
        """
        actions = {
            'accel': self._accel, 'brake': self._brake,
            'gear': self._gear, 'steer': self._steering,
            'clutch': self._clutch, 'focus': self._focus,
            'meta': self._meta
        }

        return Protocol.encode(actions)

    @property
    def accel(self) -> float:
        return self._accel

    @accel.setter
    def accel(self, value: float):
        """
        Range: [0, 1].
        """
        if value < 0:
            self._accel = 0
        elif value > 1:
            self._accel = 1
        else:
            self._accel = value

    @property
    def brake(self) -> float:
        return self._brake

    @brake.setter
    def brake(self, value: float):
        """
        Range: [0, 1].
        """
        if value < 0:
            self._brake = 0
        elif value > 1:
            self._brake = 1
        else:
            self._brake = value

    @property
    def clutch(self) -> float:
        return self._clutch

    @clutch.setter
    def clutch(self, value: float):
        """
        Range: [0, 1].
        """
        if value < 0:
            self._clutch = 0
        elif value > 1:
            self._clutch = 1
        else:
            self._clutch = value

    @property
    def gear(self) -> int:
        return self._gear

    @gear.setter
    def gear(self, value: int):
        """
        Range: {-1, 0, ..., 6}.
        """
        if value in [x for x in range(-1, 7)]:
            self._gear = value

    @property
    def steering(self) -> float:
        return self._steering

    @steering.setter
    def steering(self, value: float):
        """
        Range: [-1, 1].
        """
        if value < -1:
            self._steering = -1
        elif value > 1:
            self._steering = 1
        else:
            self._steering = value

    @property
    def focus(self) -> float:
        return self._focus

    @focus.setter
    def focus(self, value: float):
        """
        Range: [-90, 90].
        """
        if value < -90:
            self._focus = -90
        elif value > 90:
            self._focus = 90
        else:
            self._focus = value

    @property
    def meta(self) -> int:
        return self._meta

    @meta.setter
    def meta(self, value: int):
        """
        Range: {0, 1}.
        """
        if value in [0, 1]:
            self._meta = value
