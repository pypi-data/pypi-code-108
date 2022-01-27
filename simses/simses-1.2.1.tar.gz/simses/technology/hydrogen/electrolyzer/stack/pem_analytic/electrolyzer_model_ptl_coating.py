from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.electrolyzer_model import \
    PemElectrolyzerMultiDimAnalytic


class PemElectrolyzerMultiDimAnalyticPtlCoating(PemElectrolyzerMultiDimAnalytic):
    """ PEM Electrolyzer with Pt-coated Ti-PTL at anode site, which prevents the cyclic increase of its resistance """
    def __init__(self, electrolyzer_maximal_power: float, electrolyzer_data_config: ElectrolyzerDataConfig):
        super().__init__(electrolyzer_maximal_power, electrolyzer_data_config)
