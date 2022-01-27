import math

from numpy import sign

from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter


class AcDcConverterIdenticalStacked(AcDcConverter):

    def __init__(self, number_converters: int, switch_value: float, acdc_converter: AcDcConverter, power_electronics_config=None):
        super().__init__(acdc_converter.max_power)
        self.__NUMBER_CONVERTERS: int = number_converters
        self.__SWITCH_VALUE: float = switch_value  # ratio power over rated power
        self.__MAX_POWER_INDIVIDUAL: float = acdc_converter.max_power / number_converters
        self.__converters: [AcDcConverter] = list()
        for converter in range(number_converters):
            self.__converters.append(acdc_converter.create_instance(self.__MAX_POWER_INDIVIDUAL, power_electronics_config))

    def to_ac(self, power: float, voltage: float) -> float:
        if power >= 0.0:
            return 0.0
        power_individual = iter(self.__power_splitter(power))
        power_individual_dc: [float] = list()
        for converter in self.__converters:
            converter: AcDcConverter = converter
            power_individual_dc.append(converter.to_ac(next(power_individual), voltage))
        return sum(power_individual_dc)

    def to_dc(self, power: float, voltage: float) -> float:
        if power <= 0.0:
            return 0.0
        power_individual = iter(self.__power_splitter(power))
        power_individual_dc: [float] = list()
        for converter in self.__converters:
            converter: AcDcConverter = converter
            power_individual_dc.append(converter.to_dc(next(power_individual), voltage))
        return sum(power_individual_dc)

    def to_dc_reverse(self, dc_power: float, voltage: float) -> float:
        if dc_power <= 0.0:
            return 0.0
        power_individual = iter(self.__power_splitter(dc_power))
        power_individual_dc: [float] = list()
        for converter in self.__converters:
            converter: AcDcConverter = converter
            power_individual_dc.append(converter.to_dc_reverse(next(power_individual), voltage))
        return sum(power_individual_dc)

    def to_ac_reverse(self, dc_power: float, voltage: float) -> float:
        if dc_power >= 0:
            return 0.0
        power_individual = iter(self.__power_splitter(dc_power))
        power_individual_dc: [float] = list()
        for converter in self.__converters:
            converter: AcDcConverter = converter
            power_individual_dc.append(converter.to_ac_reverse(next(power_individual), voltage))
        return sum(power_individual_dc)

    def __power_splitter(self, power: float) -> list:
        switch_value = self.__SWITCH_VALUE
        power_individual: [float] = [0.0] * self.__NUMBER_CONVERTERS
        if abs(power) > self.max_power:
            for converter in range(self.__NUMBER_CONVERTERS):
                power_individual[converter] = self.__MAX_POWER_INDIVIDUAL * sign(power)
        elif abs(power) > self.max_power * switch_value:
            equal_distributed_power: float = abs(power) / self.__NUMBER_CONVERTERS
            for converter in range(self.__NUMBER_CONVERTERS):
                power_individual[converter] = max(0.0, min(equal_distributed_power, self.__MAX_POWER_INDIVIDUAL)) * sign(power)
        else:
            remaining_power: float = abs(power)
            max_individual_power: float = self.__MAX_POWER_INDIVIDUAL * switch_value
            number_converters_activated: int = min(math.ceil(remaining_power / max_individual_power), self.__NUMBER_CONVERTERS)
            equal_distributed_power: float = remaining_power / number_converters_activated
            for converter in range(self.__NUMBER_CONVERTERS):
                individual_power: float = max(0.0, min(equal_distributed_power, max_individual_power, remaining_power))
                power_individual[converter] = individual_power * sign(power)
                remaining_power -= individual_power
        return power_individual

    @property
    def volume(self) -> float:
        volume: float = 0.0
        for converter in self.__converters:
            volume += converter.volume
        return volume

    @property
    def mass(self):
        mass: float = 0.0
        for converter in self.__converters:
            mass += converter.mass
        return mass

    @property
    def surface_area(self) -> float:
        surface_area: float = 0.0
        for converter in self.__converters:
            surface_area += converter.surface_area
        return surface_area

    def close(self) -> None:
        for converter in self.__converters:
            converter.close()

    @classmethod
    def create_instance(cls, max_power: float, power_electronics_config=None):
        pass

