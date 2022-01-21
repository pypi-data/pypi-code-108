'''_1020.py

NamedPlanetSideBandAmplitudeFactor
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NAMED_PLANET_SIDE_BAND_AMPLITUDE_FACTOR = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'NamedPlanetSideBandAmplitudeFactor')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedPlanetSideBandAmplitudeFactor',)


class NamedPlanetSideBandAmplitudeFactor(_0.APIBase):
    '''NamedPlanetSideBandAmplitudeFactor

    This is a mastapy class.
    '''

    TYPE = _NAMED_PLANET_SIDE_BAND_AMPLITUDE_FACTOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedPlanetSideBandAmplitudeFactor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetary_sidebands_amplitude_factor(self) -> 'float':
        '''float: 'PlanetarySidebandsAmplitudeFactor' is the original name of this property.'''

        return self.wrapped.PlanetarySidebandsAmplitudeFactor

    @planetary_sidebands_amplitude_factor.setter
    def planetary_sidebands_amplitude_factor(self, value: 'float'):
        self.wrapped.PlanetarySidebandsAmplitudeFactor = float(value) if value else 0.0
