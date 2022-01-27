from simses.commons.config.simulation.system import StorageSystemConfig
from simses.system.housing.abstract_housing import Housing
from simses.system.housing.layer import Layer


class FortyFtContainer(Housing):

    def __init__(self, housing_configuration: list, temperature: float = None):

        # Get optional user-defined values required for this class or use default values
        try:
            high_cube: bool = bool(housing_configuration[StorageSystemConfig.HOUSING_HIGH_CUBE])
        except (ValueError, IndexError, TypeError):
            high_cube = False
        try:
            azimuth: float = float(housing_configuration[StorageSystemConfig.HOUSING_AZIMUTH])
        except (ValueError, IndexError, TypeError):
            azimuth = 0
        try:
            outer_layer_absorptivity: float = float(housing_configuration[StorageSystemConfig.HOUSING_ABSORPTIVITY])
        except (ValueError, IndexError, TypeError):
            outer_layer_absorptivity = 0.15
        try:
            ground_albedo: float = float(housing_configuration[StorageSystemConfig.HOUSING_GROUND_ALBEDO])
        except (ValueError, IndexError, TypeError):
            ground_albedo = 0.2

        if temperature is None:
            temperature = 298.15  # default value = 25 °C

        # Container external dimensions (from mtcontainer)
        outer_length = 12.192  # m
        outer_breadth = 2.438  # m
        if high_cube:
            outer_height = 2.891  # m
        else:
            outer_height = 2.591  # m

        # Wall layer thicknesses
        thickness_inner_layer = 0.001  # m, L1 = layer 1 - Aluminium
        thickness_mid_layer = 0.050  # m, L2 = Layer 2 - Rock wool
        thickness_outer_layer = 0.0016  # m, L3 = Layer 3 - steel (1.6 mm)
        depth_corrugation = 0.03  # m (0.254)

        # Container internal dimensions
        inner_length = outer_length - 2 * (thickness_inner_layer + thickness_mid_layer + thickness_outer_layer + depth_corrugation)  # in m
        inner_breadth = outer_breadth - 2 * (thickness_inner_layer + thickness_mid_layer + thickness_outer_layer + depth_corrugation)  # m
        inner_height = outer_height - 2 * (thickness_inner_layer + thickness_mid_layer + thickness_outer_layer + depth_corrugation)  # m

        # Densities of layers
        density_inner_layer_material = 2700  # kg/m3 (for Aluminium)
        density_mid_layer_material = 100  # kg/m3 (for Rock wool)
        density_outer_layer_material = 8050  # kg/m3 (for Steel)

        # Container material thermal characteristics
        thermal_conductivity_inner_layer = 237  # W/mK  (for Aluminium)
        thermal_conductivity_mid_layer = 0.050  # W/mK (for Rock wool)
        thermal_conductivity_outer_layer = 14.4  # W/mK (for Steel - Stainless, Type 304)
        specific_heat_inner_layer = 910  # J/kgK (for Aluminium)
        specific_heat_mid_layer = 840  # J/kgK (for Rock wool)
        specific_heat_outer_layer = 500  # J/kgK (for Steel - Stainless, Type 304)
        convection_coefficient_air_inner_layer = 30  # W/m2K, Convection coefficient for convection from air to L1 material (exemplary value)
        convection_coefficient_air_outer_layer = 30  # W/m2K, Convection coefficient for convection from L3 material to air (exemplary value)

        # Container Orientation and Surroundings
        self.__azimuth = azimuth
        self.__albedo = ground_albedo

        # Initialize layer properties

        # Layer 1 attributes (inner layer - Aluminium)
        inner_layer_attributes = dict()
        inner_layer_attributes[Layer.LENGTH] = inner_length  # m
        inner_layer_attributes[Layer.BREADTH] = inner_breadth  # m
        inner_layer_attributes[Layer.HEIGHT] = inner_height  # m
        inner_layer_attributes[Layer.THICKNESS] = thickness_inner_layer  # m
        inner_layer_attributes[Layer.DENSITY] = density_inner_layer_material  # kg/m3 (for Aluminium)
        inner_layer_attributes[Layer.THERMAL_CONDUCTIVITY] = thermal_conductivity_inner_layer  # W/mK  (for Aluminium)
        inner_layer_attributes[Layer.SPECIFIC_HEAT] = specific_heat_inner_layer  # J/kgK (for Aluminium)
        inner_layer_attributes[Layer.CONVECTION_COEFFICIENT] = convection_coefficient_air_inner_layer  # W/m2K
        inner_layer_attributes[Layer.ABSORPTIVITY] = None  # dimensionless
        inner_layer_attributes[Layer.TEMPERATURE] = temperature  # Initialized with ambient temperature
        inner_layer = Layer(inner_layer_attributes)

        # Layer 2 attributes (mid layer - Rock Wool)
        mid_layer_attributes = dict()
        mid_layer_attributes[Layer.LENGTH] = (outer_length + inner_length) / 2  # m
        mid_layer_attributes[Layer.BREADTH] = (outer_breadth + inner_breadth) / 2  # m
        mid_layer_attributes[Layer.HEIGHT] = (outer_height + inner_height) / 2  # m
        mid_layer_attributes[Layer.THICKNESS] = thickness_mid_layer  # m
        mid_layer_attributes[Layer.DENSITY] = density_mid_layer_material  # kg/m3 (for Rock Wool)
        mid_layer_attributes[Layer.THERMAL_CONDUCTIVITY] = thermal_conductivity_mid_layer  # W/mK  (for Rock Wool)
        mid_layer_attributes[Layer.SPECIFIC_HEAT] = specific_heat_mid_layer  # J/kgK (for Rock Wool)
        mid_layer_attributes[Layer.CONVECTION_COEFFICIENT] = None  # W/m2K
        mid_layer_attributes[Layer.ABSORPTIVITY] = None  # dimensionless
        mid_layer_attributes[Layer.TEMPERATURE] = temperature  # Initialized with ambient temperature
        mid_layer = Layer(mid_layer_attributes)

        # Layer 3 attributes (outer layer - steel)
        outer_layer_attributes = dict()
        outer_layer_attributes[Layer.LENGTH] = outer_length  # m
        outer_layer_attributes[Layer.BREADTH] = outer_breadth  # m
        outer_layer_attributes[Layer.HEIGHT] = outer_height  # m
        outer_layer_attributes[Layer.THICKNESS] = thickness_outer_layer  # m
        outer_layer_attributes[Layer.DENSITY] = density_outer_layer_material  # kg/m3 (for Steel)
        outer_layer_attributes[Layer.THERMAL_CONDUCTIVITY] = thermal_conductivity_outer_layer  # W/mK  (for Steel)
        outer_layer_attributes[Layer.SPECIFIC_HEAT] = specific_heat_outer_layer  # J/kgK (for Steel)
        outer_layer_attributes[Layer.CONVECTION_COEFFICIENT] = convection_coefficient_air_outer_layer  # W/m2K
        outer_layer_attributes[Layer.ABSORPTIVITY] = outer_layer_absorptivity  # dimensionless
        outer_layer_attributes[Layer.TEMPERATURE] = temperature  # Initialized with ambient temperature
        outer_layer = Layer(outer_layer_attributes)

        super().__init__(inner_layer, mid_layer, outer_layer, default_scale=1)

    @property
    def azimuth(self) -> float:
        return self.__azimuth

    @property
    def albedo(self) -> float:
        return self.__albedo


# if __name__ == '__main__':  # Enables isolated debugging and execution of test cases
#     print("This only executes when %s is executed rather than imported" % __file__)
#     amb_model = ConstantAmbientTemperature()
#     container = FortyFtContainer(amb_model)
#     vol = container.internal_air_volume
#     print(vol)
