'''_306.py

PlanetaryDetail
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears import _305
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLANETARY_DETAIL = python_net_import('SMT.MastaAPI.Gears', 'PlanetaryDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryDetail',)


class PlanetaryDetail(_0.APIBase):
    '''PlanetaryDetail

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planet_diameter(self) -> 'float':
        '''float: 'PlanetDiameter' is the original name of this property.'''

        return self.wrapped.PlanetDiameter

    @planet_diameter.setter
    def planet_diameter(self, value: 'float'):
        self.wrapped.PlanetDiameter = float(value) if value else 0.0

    @property
    def number_of_planets(self) -> 'int':
        '''int: 'NumberOfPlanets' is the original name of this property.'''

        return self.wrapped.NumberOfPlanets

    @number_of_planets.setter
    def number_of_planets(self, value: 'int'):
        self.wrapped.NumberOfPlanets = int(value) if value else 0

    @property
    def regularly_spaced_planets(self) -> 'bool':
        '''bool: 'RegularlySpacedPlanets' is the original name of this property.'''

        return self.wrapped.RegularlySpacedPlanets

    @regularly_spaced_planets.setter
    def regularly_spaced_planets(self, value: 'bool'):
        self.wrapped.RegularlySpacedPlanets = bool(value) if value else False

    @property
    def first_planet_angle(self) -> 'float':
        '''float: 'FirstPlanetAngle' is the original name of this property.'''

        return self.wrapped.FirstPlanetAngle

    @first_planet_angle.setter
    def first_planet_angle(self, value: 'float'):
        self.wrapped.FirstPlanetAngle = float(value) if value else 0.0

    @property
    def planet_delta_angles(self) -> 'List[_305.NamedPlanetAngle]':
        '''List[NamedPlanetAngle]: 'PlanetDeltaAngles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetDeltaAngles, constructor.new(_305.NamedPlanetAngle))
        return value
