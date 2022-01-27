import pandas as pd

from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig


class ParametersAlkalineElectrolyzerFit:

    def __init__(self, electrolyzer_data_config: ElectrolyzerDataConfig):
        file = electrolyzer_data_config.alkaline_electrolyzer_fit_para_file
        correction_parameters = pd.read_csv(file)
        self.__corr_parameters = correction_parameters.iloc[:, 0]

    # Regression Parameters for Zirfon Membrane Resistance
    @property
    def zirfon1(self) -> float:
        return 2.085e-5

    @property
    def zirfon2(self) -> float:
        return -0.01603

    @property
    def zirfon3(self) -> float:
        return 3.188

    # Curve Fitting Correction Factors
    @property
    def ac(self) -> float:
        return self.__corr_parameters[0]

    @property
    def bc(self) -> float:
        return self.__corr_parameters[1]

    @property
    def cc(self) -> float:
        return self.__corr_parameters[2]

    @property
    def aa(self) -> float:
        return self.__corr_parameters[3]

    @property
    def ba(self) -> float:
        return self.__corr_parameters[4]

    @property
    def ca(self) -> float:
        return self.__corr_parameters[5]

    @property
    def r1(self) -> float:
        return self.__corr_parameters[6]

    @property
    def r2(self) -> float:
        return self.__corr_parameters[7]

    @property
    def r3(self) -> float:
        return self.__corr_parameters[8]

    @property
    def a1(self) -> float:
        return self.__corr_parameters[9]

    @property
    def a2(self) -> float:
        return self.__corr_parameters[10]
