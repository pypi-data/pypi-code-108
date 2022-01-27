from simses.system.power_electronics.acdc_converter.fix_efficiency import FixEfficiencyAcDcConverter


class NoLossAcDcConverter(FixEfficiencyAcDcConverter):

    def __init__(self, max_power: float):
        super().__init__(max_power, efficiency=1.0)

    @classmethod
    def create_instance(cls, max_power: float, power_electronics_config=None):
        return NoLossAcDcConverter(max_power)
