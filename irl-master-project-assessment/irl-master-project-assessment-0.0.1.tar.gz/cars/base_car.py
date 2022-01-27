class BaseCar:
    MAX_SPEED = 50
    ACC = 5
    BRAKE_EFF = -10
    REVERSE = 'Reverse'
    PARK = 'Park'
    DRIVES = 'Drive'

    # Initializes an average car
    def __init__(self):
        self.home = 0.0
        self.engine_on = False
        self.lights_on = False
        self.odometer = 0.0
        self.speed = 0.0
        self.gear = self.PARK

    # Switches engine on and initializes 'home'
    def on(self):
        self.engine_on = True

    # Switches engine off
    def off(self):
        # Checks if car is still moving
        if self.speed == 0.0:
            self.engine_on = False
        else:
            raise Exception("Can't turn engine off! Car is still moving")

    # Adds gas to engine. Responsible for acceleration
    def gas(self, time):
        # Checks engine is on
        if self.engine_on:
            speed = self.ACC * time
            self.speed += speed
            # Checks if maximum speed is reached. Increments current speed or assigns maximum otherwise
            if self.speed > self.MAX_SPEED:
                self.speed = self.MAX_SPEED
        else:
            raise Exception("Can't start gas! Engine off")

    # Propels the car forward (Average car)
    def drive(self, time):
        # Checks engine is on and that car is accelerated(has speed)
        if self.engine_on:
            if self.speed > 0:
                # Calculates total distance driven. Considers absolute speed value
                distance = self.speed * time
                self.odometer += distance

                # If car is moving in reverse
                if self.gear == self.REVERSE:
                    self.home -= distance
                    self.home = abs(self.home)
                else:
                    # Calculates distance from 'home'
                    self.home += distance
                    if self.gear != self.REVERSE:
                        # Sets gear to 'Drive' mode
                        self.gear = self.DRIVES
            else:
                raise Exception("Car speed is 0!")
        else:
            raise Exception("Can't drive! Engine off")

    # Brings car to a complete stop
    def halt(self):
        self.speed = 0
        self.gear = self.PARK

    # Slows down (deccelerates) car
    def brake(self, time):
        # Checks engine is on
        if self.engine_on:
            speed = self.BRAKE_EFF * time
            self.speed += speed
            # Checks if car has stopped (As average car cannot reverse)
            if self.speed < 0:
                # Sets gear to 'Park' mode if speed is 0
                self.speed = 0
                self.gear = self.PARK
        else:
            raise Exception("Cant brake! Engine is off")

    # Turns the headlights on/off
    def headlights(self):
        # Toggles the on/off state
        self.lights_on = not self.lights_on

    # Shows current car stats
    def dashboard(self):
        states = {True: 'on', False: 'off'}

        stats = f'engine: {states[self.engine_on]}\n'
        stats += f'lights: {states[self.lights_on]}\n'
        stats += f'speed: {self.speed}m/s\n'
        stats += f'odometer: {self.odometer}m\n'
        stats += f'home: {self.home}m\n'
        stats += f'gear: {self.gear}\n'

        print(stats)

    def __str__(self):
        self.dashboard()
