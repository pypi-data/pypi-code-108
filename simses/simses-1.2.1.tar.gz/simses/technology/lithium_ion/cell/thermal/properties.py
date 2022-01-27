class ThermalCellProperties:

    """
    ThermalCellProperties inherits all necessary data for describing the thermal behaviour of a cell.
    """

    def __init__(self, min_temperature: float, max_temperature: float, mass: float,
                 specific_heat: float, convection_coeffecient: float):
        """
        Constructor for ThermalCellProperties

        Parameters
        ----------
        min_temperature :
            minimum allowed temperature for the cell in K
        max_temperature :
            maximum allowed temperature for the cell in K
        mass :
            mass of one cell in kg
        specific_heat :
            specific heat of the cell in J/kgK
        convection_coeffecient :
            convection coefficient in W/m2K
        """
        self.__MIN_TEMPERATURE: float = min_temperature
        self.__MAX_TEMPERATURE: float = max_temperature
        self.__MASS: float = mass
        self.__SPECIFIC_HEAT: float = specific_heat
        self.__CONVECTION_COEFFICIENT: float = convection_coeffecient

    def get_min_temperature(self) -> float:
        """

        Returns
        -------
        float:
            minimum allowed temperature for the cell in K
        """
        return self.__MIN_TEMPERATURE

    def get_max_temperature(self) -> float:
        """

        Returns
        -------
        float:
            maximum allowed temperature for the cell in K
        """
        return self.__MAX_TEMPERATURE

    def get_specific_heat(self) -> float:
        """

        Returns
        -------
        float:
            specific heat of the cell in J/kgK
        """
        return self.__SPECIFIC_HEAT

    def get_convection_coefficient(self) -> float:
        """

        Returns
        -------
        float:
            convection coefficient in W/m2K
        """
        return self.__CONVECTION_COEFFICIENT

    def get_mass(self) -> float:
        """

        Returns
        -------
        float:
            mass of one cell in kg
        """
        return self.__MASS
