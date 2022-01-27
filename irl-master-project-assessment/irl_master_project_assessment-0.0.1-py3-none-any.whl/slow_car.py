from cars.base_car import BaseCar


class SlowCar(BaseCar):
    MAX_SPEED = BaseCar.MAX_SPEED * 0.75
    ACC = BaseCar.ACC * 0.75
    BRAKE_EFF = BaseCar.BRAKE_EFF * 2

    def dashboard(self):
        print('Slow Car Stats:')
        BaseCar.dashboard(self)
