from .protocol import Protocol


class State:
    def __init__(self, message: str):
        """
        Class representing the available sensors.

        Fields:
            sensors (dict)              Dictionary with all sensors below.
            angle (float)               Angle between the car direction and the direction of the track axis.
            current_lap_time (float)    Time elapsed during current lap.
            damage (float)              Current damage to the car (the higher is the value the higher is the damage).
            distance_from_start (float) Distance of the car from the start line along the track line.
            distance_raced (float)      Distance covered by the car from the beginning of the race.
            focus (float)               Vector of 5 range finder sensors: each sensor returns the distance between the
                                        track edge and the car within a range of 200 meters.
            fuel (float)                Current fuel level.
            gear (int)                  Current gear: -1 is reverse, 0 is neutral and the gear from 1 to 6.
            last_lap_time (float)       Time to complete the last lap.
            opponents (float)           Vector of 36 opponent sensors: each sensor covers a span of 10 degrees within a
                                        range of 200 meters and returns the distance of the closest opponent in the
                                        covered area.
            race_position (int)         Position in the race with respect to other cars.
            rpm (float)                 Number of rotation per minute of the car engine.
            speed_X (float)             Speed of the car along the longitudinal axis of the car.
            speed_Y (float)             Speed of the car along the transverse axis of the car.
            speed_Z (float)             Speed of the car along the Z axis of the car.
            track (float)               Vector of 19 range finder sensors: each sensor returns the distance between the
                                        track edge and the car within a range of 200 meters.
            track_position (float)      Distance between the car and the track axis.
            wheel_spin_velocity (float) Vector of 4 sensors representing the rotation speed of wheels.
            z (float)                   Distance of the car mass center from the surface of the track along the Z axis.
        """
        self.sensors = Protocol.decode(message)

        self.angle = self.__set('angle')
        self.current_lap_time = self.__set('curLapTime')
        self.damage = self.__set('damage')
        self.distance_from_start = self.__set('distFromStart')
        self.distance_raced = self.__set('distRaced')
        self.focus = self.__set('focus')
        self.fuel = self.__set('fuel')
        self.gear = self.__set('gear')
        self.last_lap_time = self.__set('lastLapTime')
        self.opponents = self.__set('opponents')
        self.race_position = self.__set('racePos')
        self.rpm = self.__set('rpm')
        self.speed_X = self.__set('speedX')
        self.speed_Y = self.__set('speedY')
        self.speed_Z = self.__set('speedZ')
        self.track = self.__set('track')
        self.track_position = self.__set('trackPos')
        self.wheel_spin_velocity = self.__set('wheelSpinVel')
        self.z = self.__set('z')

    def __str__(self):
        self.sensors = {
            'angle': self.angle, 'curLapTime': self.current_lap_time,
            'damage': self.damage, 'distFromStart': self.distance_from_start,
            'distRaced': self.distance_raced, 'focus': self.focus,
            'fuel': self.fuel, 'gear': self.gear,
            'lastLapTime': self.last_lap_time, 'opponents': self.opponents,
            'racePos': self.race_position, 'rpm': self.rpm,
            'speedX': self.speed_X, 'speedY': self.speed_Y,
            'speedZ': self.speed_Z, 'track': self.track,
            'trackPos': self.track_position, 'wheelSpinVel': self.wheel_spin_velocity,
            'z': self.z
        }

        return Protocol.encode(self.sensors)

    def __set(self, sensor: str):
        try:
            signal = self.sensors[sensor]
        except KeyError:
            return None

        if isinstance(signal, list):
            return [float(s) for s in signal]
        else:
            return float(signal)
