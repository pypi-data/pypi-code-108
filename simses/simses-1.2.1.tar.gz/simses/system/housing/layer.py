class Layer:

    """
    Class Layer specifies and controls the attributes of each layer of the wall of a shipping container (Housing)
    """

    # Layer attribute names
    LENGTH: str = 'length'
    BREADTH: str = 'breadth'
    HEIGHT: str = 'height'
    THICKNESS: str = 'thickness'
    DENSITY: str = 'density'
    THERMAL_CONDUCTIVITY: str = 'thermal_conductivity'
    SPECIFIC_HEAT: str = 'specific_heat'
    CONVECTION_COEFFICIENT: str = 'convection_coefficient_air'
    ABSORPTIVITY: str = 'absorptivity'
    TEMPERATURE: str = 'temperature'

    def __init__(self, layer_attributes: dict):
        self.__length = layer_attributes[self.LENGTH]
        self.__breadth = layer_attributes[self.BREADTH]
        self.__height = layer_attributes[self.HEIGHT]
        self.__thickness = layer_attributes[self.THICKNESS]
        self.__density = layer_attributes[self.DENSITY]
        self.__thermal_conductivity = layer_attributes[self.THERMAL_CONDUCTIVITY]
        self.__specific_heat = layer_attributes[self.SPECIFIC_HEAT]
        self.__convection_coefficient_air = layer_attributes[self.CONVECTION_COEFFICIENT]
        self.__absorptivity = layer_attributes[self.ABSORPTIVITY]
        self.__temperature = layer_attributes[self.TEMPERATURE]

        self.__surface_area_long_side = self.__length * self.__height
        self.__surface_area_roof = self.__length * self.__breadth
        self.__surface_area_short_side = self.__breadth * self.__height
        self.__surface_area_total = 2 * (self.__surface_area_long_side + self.__surface_area_short_side + self.__surface_area_roof)
        self.__material_volume = self.__surface_area_total * self.__thickness
        self.__mass = self.__material_volume * self.__density
        self.__scale_factor = 1

    def update_scale(self):
        self.__scale_factor += 1

    @property
    def length(self) -> float:
        return self.__length

    @property
    def breadth(self) -> float:
        return self.__breadth

    @property
    def height(self) -> float:
        return self.__height

    @property
    def thickness(self) -> float:
        return self.__thickness

    @property
    def mass(self) -> float:
        return self.__mass

    @property
    def thermal_conductivity(self) -> float:
        return self.__thermal_conductivity

    @property
    def specific_heat(self) -> float:
        return self.__specific_heat

    @property
    def convection_coefficient_air(self) -> float:
        return self.__convection_coefficient_air

    @property
    def absorptivity(self) -> float:
        return self.__absorptivity

    @property
    def surface_area_long_side(self) -> float:
        return self.__surface_area_long_side * self.__scale_factor

    @property
    def surface_area_short_side(self) -> float:
        return self.__surface_area_short_side * self.__scale_factor

    @property
    def surface_area_roof(self) -> float:
        return self.__surface_area_roof * self.__scale_factor

    @property
    def surface_area_total(self) -> float:
        return self.__surface_area_total * self.__scale_factor

    @property
    def temperature(self) -> float:
        return self.__temperature
