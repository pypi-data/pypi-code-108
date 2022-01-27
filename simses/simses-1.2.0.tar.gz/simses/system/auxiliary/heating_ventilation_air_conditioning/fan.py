class Fan:
    """
    The fan class is an attribute of the HVAC classes
    Data sheet source:
    https://www.kaltra.com/wp-content/uploads/2020/01/SB_Delta_CW-CWU_Ver.5.0_EN.pdf
    """

    def __init__(self):

        self.__rated_airflow = 3.61  # m3/s
        self.__rated_power = 2560.0  # W

        # Initialize
        self.__airflow = 0.0  # m3/s
        self.__electricity_consumption = 0.0  # W

    def run(self, airflow) -> None:
        # physical energy conversion equations here
        self.__airflow = airflow
        self.__electricity_consumption = float(self.__rated_power * ((self.__airflow / self.__rated_airflow) ** 2))

    @property
    def electricity_consumption(self) -> float:
        return self.__electricity_consumption

    @property
    def rated_airflow(self) -> float:
        return self.__rated_airflow

    @property
    def airflow(self) -> float:
        return self.__airfow
