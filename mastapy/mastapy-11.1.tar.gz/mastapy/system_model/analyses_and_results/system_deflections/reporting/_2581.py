'''_2581.py

PlanetCarrierWindup
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.reporting import _2582
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_WINDUP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Reporting', 'PlanetCarrierWindup')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierWindup',)


class PlanetCarrierWindup(_0.APIBase):
    '''PlanetCarrierWindup

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_WINDUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierWindup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def reference_socket(self) -> 'str':
        '''str: 'ReferenceSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceSocket

    @property
    def other_planet_carrier(self) -> 'str':
        '''str: 'OtherPlanetCarrier' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OtherPlanetCarrier

    @property
    def other_socket(self) -> 'str':
        '''str: 'OtherSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OtherSocket

    @property
    def average_torsional_wind_up(self) -> 'float':
        '''float: 'AverageTorsionalWindUp' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageTorsionalWindUp

    @property
    def average_tangential_tilt(self) -> 'float':
        '''float: 'AverageTangentialTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageTangentialTilt

    @property
    def average_radial_tilt(self) -> 'float':
        '''float: 'AverageRadialTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageRadialTilt

    @property
    def average_axial_deflection(self) -> 'float':
        '''float: 'AverageAxialDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageAxialDeflection

    @property
    def pin_wind_ups(self) -> 'List[_2582.PlanetPinWindup]':
        '''List[PlanetPinWindup]: 'PinWindUps' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PinWindUps, constructor.new(_2582.PlanetPinWindup))
        return value
