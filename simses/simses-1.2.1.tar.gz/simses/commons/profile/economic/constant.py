from simses.commons.profile.economic.market import MarketProfile


class ConstantPrice(MarketProfile):

    def __init__(self, price: float):
        super(ConstantPrice, self).__init__()
        self.__price: float = price

    def next(self, time: float) -> float:
        return self.__price

    def initialize_profile(self) -> None:
        pass

    def profile_data_to_list(self, sign_factor=1) -> ([float], [float]):
        pass

    def close(self):
        pass
