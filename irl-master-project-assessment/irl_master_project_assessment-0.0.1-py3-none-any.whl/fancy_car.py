from cars.base_car import BaseCar


class FancyCar(BaseCar):
    MAX_SPEED = BaseCar.MAX_SPEED * 2
    ACC = BaseCar.ACC
    BRAKE_EFF = BaseCar.BRAKE_EFF

    # Drives/Reverses gear
    def changeGear(self, gear_direction):
        if self.speed == 0:
            direction = str.lower(gear_direction)
            if direction == 'reverse':
                self.gear = self.REVERSE
            elif direction == 'park':
                print(f'Already in Park Mode: {self.gear}')
            elif direction == 'drive':
                self.gear = self.DRIVES
            else:
                raise ValueError('Wrong Gear Value!')
        else:
            raise Exception('Can\'t switch gears! Speed is greater than 0')

    # Creates a horn sound
    def horn(self):
        print("Bleep Bleep!")

    # Shows current car stats
    def dashboard(self):
        print('Fancy Car Stats:')
        states = {True: 'on', False: 'off'}

        stats = f'engine: {states[self.engine_on]}\n'
        stats += f'lights: {states[self.lights_on]}\n'
        stats += f'speed: {self.speed}m/s\n'
        stats += f'odometer: {self.odometer}m\n'
        stats += f'home: {self.home}m\n'
        stats += f'direction: {self.gear}\n'

        print(stats)
