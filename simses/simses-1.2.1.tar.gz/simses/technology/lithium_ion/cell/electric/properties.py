class ElectricalCellProperties:

    """
    ElectricalCellProperties inherits all necessary data for describing the electrical behaviour of a cell.
    """

    def __init__(self, cell_voltage: float, cell_capacity: float, min_voltage: float, max_voltage: float,
                 max_charge_rate: float, max_discharge_rate: float, self_discharge_rate: float,
                 coulomb_efficiency: float):
        """
        Constructor of ElectricalCellProperties

        Parameters
        ----------
        cell_voltage :
            nominal voltage of one cell in V
        cell_capacity :
            nominal capacity of one cell in V
        min_voltage :
            minimum allowed voltage of one cell in V
        max_voltage :
            maximum allowed voltage of one cell in V
        max_charge_rate :
            maximum allowed charge rate in 1/h (C-rate)
        max_discharge_rate :
            maximum allowed discharge rate in 1/h (C-rate)
        self_discharge_rate :
            self discharge rate in p.u. as X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
        coulomb_efficiency :
            coulomb efficiency of the cell in p.u.
        """
        self.__NOMINAL_VOLTAGE: float = cell_voltage  # V
        self.__NOMINAL_CAPACITY: float = cell_capacity  # Ah
        self.__MAX_VOLTAGE: float = max_voltage  # V
        self.__MIN_VOLTAGE: float = min_voltage  # V
        self.__MAX_CHARGE_RATE: float = max_charge_rate  # 1/h
        self.__MAX_DISCHARGE_RATE: float = max_discharge_rate  # 1/h
        self.__SELF_DISCHARGE_RATE: float = self_discharge_rate / 24.0 / 3600.0 / 100.0 # X.Xp.u-soc per second
        self.__COULOMB_EFFICIENCY: float = coulomb_efficiency  # p.u.

    def get_nominal_voltage(self) -> float:
        """

        Returns
        -------
        float:
            nominal voltage of one cell in V
        """
        return self.__NOMINAL_VOLTAGE

    def get_nominal_capacity(self) -> float:
        """

        Returns
        -------
        float:
            nominal capacity of one cell in Ah
        """
        return self.__NOMINAL_CAPACITY

    def get_max_voltage(self) -> float:
        """

        Returns
        -------
        float:
            maximum allowed voltage of one cell in V
        """
        return self.__MAX_VOLTAGE

    def get_min_voltage(self) -> float:
        """

        Returns
        -------
        float:
            minimum allowed voltage of one cell in V
        """
        return self.__MIN_VOLTAGE

    def get_max_charge_rate(self) -> float:
        """

        Returns
        -------
        float:
            maximum allowed charge rate in 1/h (C-rate)
        """
        return self.__MAX_CHARGE_RATE

    def get_max_discharge_rate(self) -> float:
        """

        Returns
        -------
        float:
            maximum allowed discharge rate in 1/h (C-rate)
        """
        return self.__MAX_DISCHARGE_RATE

    def get_self_discharge_rate(self) -> float:
        """

        Returns
        -------
        float:
            self discharge rate in Wh/s
        """
        return self.__SELF_DISCHARGE_RATE * self.get_nominal_capacity() * self.get_nominal_voltage()

    def get_coulomb_efficiency(self) -> float:
        """

        Returns
        -------
        float:
            coulomb efficiency of the cell in p.u.
        """
        return self.__COULOMB_EFFICIENCY
