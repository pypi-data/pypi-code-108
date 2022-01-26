"""Thermal modeling tools.

It models conductivity and air layers, but also radiative and convective surface phenomena. Thermal bridges can be added as well as air infiltration. The module yields thermal resistances of walls.

Author: stephane.ploix@grenoble-inp.fr
"""

import warnings
from numpy import interp
import scipy.constants


class Composition:
    """A composition is composed of successive layers related to a unit surface.

    Physical values can be added to the data on top of the class.
    """

    _conductivities = {'concrete': 1, 'glass': 1, 'wood': .2, 'plaster': .35, 'foam': .05, 'polystyrene': .039, 'brick': 0.84}
    _his = {'vertical': 7.69, 'ascending': 10, 'descending': 5.88}
    _he_wind = 5.7
    _he_constant = 11.4
    _emissivities = {'usual': .93, 'glass': .94, 'wood': .95, 'plaster': .98, 'concrete': 0.85, 'polystyrene': .97, 'brick:': .93}
    _thicknesses = (0, 5e-3, 7e-3, 10e-3, 15e-3, 25e-3, 30e-3)
    _thermal_resistances = (0, 0.11, 0.13, 0.15, 0.17, 0.18, 0.18)
    _positions = ['horizontal', 'vertical']
    volumic_masses = {'concrete': 2200, 'air': 1.204, 'wood': 350, 'glass': 2530}
    specific_heats = {'concrete': 880, 'air': 710, 'wood': 2000, 'glass': 720}

    @classmethod
    def _hi_unit(cls, position='vertical'):
        """Retirn indoor convective transmission coefficient.

        :param position: 'vertical' or 'horizontal'
        :type position: string
        :return:  the hi coefficient in W/m2.K
        :rtype: float
        """
        return cls._his[position]

    @classmethod
    def _he_unit(cls, wind_speed_in_ms=2.4):
        """
        Return outdoor convective transmission coefficient.

        :param wind_speed_in_ms: wind speed in m/s, default is to 2.4m/S
        :type wind_speed_in_ms: float
        :return: the coefficient in W/m2.K
        :rtype: float
        """
        return cls._he_wind * wind_speed_in_ms + cls._he_constant

    @classmethod
    def _hr_unit(cls, material, average_temperature_celcius=20):
        """Return radiative transmission coefficient.

        :param material: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material: str
        :param average_temperature_celcius: the temperature for which the coefficient is calculated
        :return: the coefficient in W/m2.K
        :rtype: float
        """
        if material  not in cls._emissivities:
            material = 'usual'
            warnings.warn('material '+material+'has been replaced by usual')
        return 4 * scipy.constants.sigma * cls._emissivities[material] * (average_temperature_celcius + 273.15) ** 3

    @classmethod
    def Rsout_unit(cls, material, average_temperature_celsius, wind_speed_is_m_per_sec):
        """Return outdoor convective and radiative transmission coefficient.

        :param material: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material: str
        :param average_temperature_celsius: the temperature for which the coefficient is calculated
        :type average_temperature_celsius: float
        :param wind_speed_is_m_per_sec: wind speed in m/s
        :type wind_speed_is_m_per_sec: wind spped on site
        :return: the coefficient in W/m2.K
        :rtype: float
        """
        return 1 / (cls._he_unit(wind_speed_is_m_per_sec) + Composition._hr_unit(material, average_temperature_celsius))

    @classmethod
    def Rsin_unit_vertical(cls, material, average_temperature_celsius=20):
        """Indoor convective and radiative transmission coefficient for a vertical surface.

        :param material: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material: str
        :param average_temperature_celsius: the temperature for which the coefficient is calculated
        :type average_temperature_celsius: float
        :return: the coefficient in W/m2.K
        :rtype: float
        """
        return 1 / (Composition._hi_unit('vertical') + Composition._hr_unit(material, average_temperature_celsius))

    @classmethod
    def Rsin_unit_ascending(cls, material='usual', average_temperature_celsius=20):
        """Compute an indoor air limit surface: convective and radiative transmission coefficient for a horizontal surface with ascending heat flow.

        :param material: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material: string
        :param average_temperature_celsius: the temperature for which the coefficient is calculated
        :type average_temperature_celsius: average magnitude temperature i celdius, default to 20.
        :return: the coefficient in W/m2.
        :rtype: float
        """
        return 1 / (Composition._hi_unit('ascending') + Composition._hr_unit(material, average_temperature_celsius))

    @classmethod
    def Rsin_unit_descending(cls, material='usual', average_temperature_celsius=20):
        """Compute: Indoor convective and radiative transmission coefficient for a horizontal surface with descending heat flow.

        :param material: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material: str
        :param average_temperature_celsius: the temperature for which the coefficient is calculated, default is to 20
        :type average_temperature_celsius: float
        :return: the coefficient in W/m2.K
        :rtype: float
        """
        return 1 / (Composition._hi_unit('descending') + Composition._hr_unit(material, average_temperature_celsius))

    @classmethod
    def R_air_layer_unit_resistance(cls, thickness, position, material1, material2, average_temperature_celsius=20):
        """Return the hermal resistance of an air layer depending of its position.

        :param thickness: thickness of the air layer
        :type thickness: float
        :param position: 'horizontal' or 'vertical'
        :type position: float
        :param material1: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material1: str
        :param material2: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material2: str
        :param average_temperature_celsius: the temperature for which the coefficient is calculated, default is to 20
        :type average_temperature_celsius: float
        :return: thermal resistance in K.m2/W
        :rtype: float
        """
        if thickness <= cls._thicknesses[-1]:
            return interp(thickness, cls._thicknesses, cls._thermal_resistances, left=0, right=cls._thermal_resistances[-1])
        else:
            if position == 'vertical':
                return cls.Rsin_unit_vertical(material1, average_temperature_celsius) + cls.Rsin_unit_vertical(material2, average_temperature_celsius)
            else:
                return cls.Rsin_unit_descending(material2, average_temperature_celsius) + cls.Rsin_unit_ascending(material1, average_temperature_celsius)

    @classmethod
    def R_unit_conduction(cls, thickness, material):
        """Compute the conductive resistance of an layer depending of its thickness.

        :param thickness: thickness of the layer
        :type thickness: float
        :param material: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type material: str
        :return: thermal resistance in K.m2/W
        :rtype: float
        """
        return thickness / cls._conductivities[material]

    def _R_unit_added(self, layer_material):
        """Compute unit resistance of a layer added to a composition under construction.

        :param layer_material: one string among 'usual', 'glass', 'wood', 'plaster', 'concrete' or 'polystyrene'
        :type layer_material: str
        :return: unit resistance
        :rtype: float
        """
        if not self.first_layer_indoor:
            return Composition.Rsout_unit(material=layer_material, average_temperature_celsius=self.outdoor_average_temperature, wind_speed_is_m_per_sec=self.wind_speed_is_m_per_sec)
        else:
            if self.position == 'vertical':
                return Composition.Rsin_unit_vertical(material=layer_material, average_temperature_celsius=self.indoor_average_temperature)
            elif self.position == 'horizontal':
                if not self.heating_floor:
                    return Composition.Rsin_unit_descending(material=layer_material, average_temperature_celsius=self.indoor_average_temperature)
                else:
                    return Composition.Rsin_unit_ascending(material=layer_material, average_temperature_celsius=self.indoor_average_temperature)
            raise ValueError('Unknown position')

    def __init__(self, first_layer_indoor, last_layer_indoor, position, indoor_average_temperature_in_celsius=20, outdoor_average_temperature_in_celsius=5, wind_speed_is_m_per_sec=2.4, heating_floor=False):
        """Create a composition is composed of successive layers.

        Physical values can be added to the data on top of the class.

        :param first_layer_indoor: True if first layer is indoor, False if it's outdoor and None if it's not in contact with air
        :type first_layer_indoor: bool or None
        :param last_layer_indoor: True if last layer is indoor, False if it's outdoor and None if it's not in contact with air
        :type last_layer_indoor: bool or None
        :param position: can be either 'vertical' or 'horizontal'
        :type position: str
        :param indoor_average_temperature_in_celsius: average indoor temperature used for linearization of radiative heat in Celsius, default is to 20°C
        :type indoor_average_temperature_in_celsius: float
        :param outdoor_average_temperature_in_celsius: average outdoor temperature used for linearization of radiative heat in Celsius, default is to 5°C
        :type outdoor_average_temperature_in_celsius: float
        :param wind_speed_is_m_per_sec (default is 2.4m/s): average wind speed in m/s
        :type wind_speed_is_m_per_sec: float
        :param heating_floor: True if there is a heating floor, False otherwise. Default is to False
        :type heating_floor: bool
        """
        self.position: str = position
        self.first_layer_indoor: bool = first_layer_indoor
        self.last_layer_indoor: bool = last_layer_indoor
        self.indoor_average_temperature: float = indoor_average_temperature_in_celsius
        self.outdoor_average_temperature: float = outdoor_average_temperature_in_celsius
        self.wind_speed_is_m_per_sec: float = wind_speed_is_m_per_sec
        self.heating_floor: bool = heating_floor
        self.layers = list()

    def add_layer(self, material, thickness):
        """Add a layer in the composition. First and last layers cannot be air layers.

        :param material: name of the material
        :type material: str
        :param thickness: thickness of the layer
        :type thickness: float
        """
        self.layers.append({'material': material, 'thickness': thickness})

    @property
    def R(self):
        """Compute the thermal resistance for the composition in W.m2/K.

        :return: unit resistance value (for 1m2)
        :rtype: float
        """
        _resistance = 0
        if self.first_layer_indoor is not None:
            if self.layers[0]['material'] == 'air' or self.layers[-1]['material'] == 'air':
                raise ValueError('an external layer cannot be made of air')
            _resistance += self._R_unit_added(self.layers[0]['material'])
        for l in range(len(self.layers)):
            if self.layers[l] is not None:
                if self.layers[l]['material'] == 'air':
                    radiative_resistance = (1 / Composition._hr_unit(self.layers[l-1]['material'], self.indoor_average_temperature)) + 1 / Composition._hr_unit(self.layers[l+1]['material'], self.indoor_average_temperature)
                    position = self.position
                    if self.position == 'horizontal' and self.heating_floor:
                        position = 'ascending'
                    elif self.position == 'horizontal' and not self.heating_floor:
                        position = 'descending'
                    air_layer_resistance = Composition.R_air_layer_unit_resistance(self.layers[l]['thickness'], position, self.layers[l-1]['material'], self.layers[l+1]['material'])
                    _resistance += 1 / (1 / air_layer_resistance + 1 / radiative_resistance)
                else:
                    _resistance += Composition.R_unit_conduction(self.layers[l]['thickness'], self.layers[l]['material'])
        if self.last_layer_indoor is not None:
            _resistance += self._R_unit_added(self.layers[-1]['material'])
        return _resistance

    @property
    def U(self):
        """Compute thermal transmission coefficient in W/m2.K (1/R of the unit resistance).

        :return: thermal transmission coefficient in W/m2.K
        :rtype: float
        """
        return 1/self.R

    def __str__(self):
        """Return a descriptive string.

        :return: string representative of the composition
        """
        string = 'U=%.4fW/K.m2 (R_unit=%.4fK.m2/W) composed of ' % (self.U, self.R)
        if self.first_layer_indoor is None:
            string += 'contact:'
        elif self.first_layer_indoor:
            string += 'indoor(%s):' % self.position
        else:
            string += 'outdoor(%s):' % self.position
        for layer in self.layers:
            string += '%s(%.3fm):' % (layer['material'], layer['thickness'])
        if self.last_layer_indoor is None:
            string += 'contact\n'
        elif self.last_layer_indoor:
            string += 'indoor(%s)\n' % self.position
        else:
            string += 'outdoor(%s)\n' % self.position
        return string


class Wall:
    """A wall is a set of compositions and thermal bridges of different dimensions (surface for compositions and length for thermal bridges) but also an infiltration varying from a minimum to a maximum value in m3/s."""

    def __init__(self, name):
        """Create a wall.

        :param name: name of the wall.
        :type name: str
        """
        self.name = name
        self.compositions = list()
        self.surfaces = list()
        self.bridges = list()
        self.lengths = list()
        self._infiltration_air_flow = 0
        self._max_opening_air_flow = 0

    def add_composition(self, composition, surface):
        """Add a part of wall in parallel with others defined by a composition and a surface.

        :param composition: composition of the part of wall
        :type composition: Composition
        :param surface: surface of the part of wall
        :type surface: float
        """
        self.compositions.append(composition)
        self.surfaces.append(surface)

    def add_bridge(self, psi, length):
        """Add a thermal bridge.

        :param psi: linear transmission coefficient in W/m.K
        :type psi: float
        :param length: length of the thermal bridge
        :type length: float
        """
        self.bridges.append(psi)
        self.lengths.append(length)

    def add_infiltration(self, minimum_infiltration):
        """Add a minimum infiltration air flow through the wall.

        :param minimum_infiltration: minimum infiltration air flow in m3/s
        :type minimum_infiltration: float
        """
        self._infiltration_air_flow = minimum_infiltration

    def add_max_opening_air_flow(self, maximum_infiltration):
        """Add a maximum infiltration air flow reached when opening ration is equal to 1.

        :param maximum_infiltration: maximum infiltration air flow in m3/s
        :type maximum_infiltration: float
        """
        self._max_opening_air_flow = maximum_infiltration

    def air_volumic_thermal_transmission(self, opening_ratio=0):
        """Return heat transmitted by volumetric exchange for an intermediate value of infiltration.

        :param opening_ratio: value between 0 and 1 changing the infiltration air flow from minimum to maximum, default is to 0.
        :type opening_ratio: float
        :return: heat transmitted by volumetric exchange in W/K
        :rtype: float
        """
        Q = self._infiltration_air_flow + opening_ratio * (self._max_opening_air_flow - self._infiltration_air_flow)
        return Composition.volumic_masses['air'] * Composition.specific_heats['air'] * Q

    def US(self, opening_ratio=0):
        """Compute the total heat loss of the wall in W/K.

        :param opening_ratio: value between 0 and 1 changing the infiltration aor flow from minimum to maximum
        :type opening_ratio: float
        :return: total heat loss of the wall in W/K
        :rtype: float
        """
        thermal_transmission_coefficient = 0
        for i in range(len(self.compositions)):
            thermal_transmission_coefficient += self.compositions[i].U * self.surfaces[i]
        for i in range(len(self.bridges)):
            thermal_transmission_coefficient += self.bridges[i] * self.lengths[i]
        thermal_transmission_coefficient += self.air_volumic_thermal_transmission(opening_ratio)
        return thermal_transmission_coefficient

    def R(self, opening_ratio=0):
        """Compute the total thermal resistance of the wall.

        :param opening_ratio: value between 0 and 1 changing the infiltration air flow from minimum to maximum
        :type opening_ratio: float
        :return: total thermal resistance of the wall in K/W
        :rtype: float
        """
        return 1 / self.US(opening_ratio)

    def __str__(self):
        """Return a descriptive string.

        :return: string representative of the wall
        """
        string = '+ Wall % s,' % self.name
        if self.US() == self.US(opening_ratio=1):
            string += 'US=%fW/K (R=%fK/W)\n' % (self.US(), self.R())
        else:
            string += 'US=%f>%fW/K (R=%f<%fK/W)\n' % (self.US(), self.US(1), self.R(), self.R(1))
        for i in range(len(self.compositions)):
            string += 'Composition(%.2fm2):' % (self.surfaces[i])
            string += self.compositions[i].__str__()
        for i in range(len(self.bridges)):
            string += 'Thermal bridge (length=%fm): psiL=%fW/K\n' % (self.lengths[i], self.lengths[i]*self.bridges[i])
        if self.air_volumic_thermal_transmission() == self.air_volumic_thermal_transmission(opening_ratio=1) == 0:
            return string + '\n'
        string += 'Infiltration loss: U=%fW/K' % self.air_volumic_thermal_transmission()
        if self.air_volumic_thermal_transmission(opening_ratio=1)!=0:
            string += '>%fW/K' % self.air_volumic_thermal_transmission(opening_ratio=1)
        return string + '\n'
