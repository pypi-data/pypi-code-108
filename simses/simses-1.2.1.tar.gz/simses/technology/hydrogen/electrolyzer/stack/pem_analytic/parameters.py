import pandas as pd

from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig


class ParametersPemElectrolyzerMultiDimAnalytic:

    def __init__(self, electrolyzer_data_config: ElectrolyzerDataConfig):
        super().__init__()
        file = electrolyzer_data_config.pem_electrolyzer_multi_dim_analytic_para_file
        correction_parameters = pd.read_csv(file)
        self.__corr_parameters = correction_parameters.iloc[:, 0]
        # parameters of quadratic regression of activation powerdensity
        self.__p10 = -0.007005
        self.__p20 = 0.01346
        self.__p11 = -0.0001083

    @property
    def q1(self) -> float:
        return self.__corr_parameters[0]

    @property
    def q3(self) -> float:
        return self.__corr_parameters[1]

    @property
    def q4(self) -> float:
        return self.__corr_parameters[2]

    @property
    def q5(self) -> float:
        return self.__corr_parameters[3]

    @property
    def q6(self) -> float:
        return self.__corr_parameters[4]

    @property
    def q7(self) -> float:
        return self.__corr_parameters[5]

    @property
    def q9(self) -> float:
        return self.__corr_parameters[6]

    @property
    def q10(self) -> float:
        return self.__corr_parameters[7]

    @property
    def q11(self) -> float:
        return self.__corr_parameters[8]

    @property
    def q12(self) -> float:
        return self.__corr_parameters[9]

    @property
    def q13(self) -> float:
        return self.__corr_parameters[10]

    @property
    def q14(self) -> float:
        return self.__corr_parameters[11]

    @property
    def q15(self) -> float:
        return self.__corr_parameters[12]

    @property
    def q17(self) -> float:
        return self.__corr_parameters[13]

    @property
    def p10(self) -> float:
        return self.__p10

    @property
    def p20(self) -> float:
        return self.__p20

    @property
    def p11(self) -> float:
        return self.__p11