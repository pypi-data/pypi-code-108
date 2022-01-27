from cars.base_car import BaseCar


class FastCar(BaseCar):
    MAX_SPEED = BaseCar.MAX_SPEED * 3
    ACC = BaseCar.ACC * 2
    BRAKE_EFF = BaseCar.BRAKE_EFF

    def dashboard(self):
        print('Fast Car Stats:')
        BaseCar.dashboard(self)
