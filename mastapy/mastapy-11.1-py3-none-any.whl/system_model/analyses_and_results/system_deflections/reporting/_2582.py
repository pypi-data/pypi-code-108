'''_2582.py

PlanetPinWindup
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLANET_PIN_WINDUP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Reporting', 'PlanetPinWindup')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetPinWindup',)


class PlanetPinWindup(_0.APIBase):
    '''PlanetPinWindup

    This is a mastapy class.
    '''

    TYPE = _PLANET_PIN_WINDUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetPinWindup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def torsional_wind_up(self) -> 'float':
        '''float: 'TorsionalWindUp' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorsionalWindUp

    @property
    def tangential_tilt(self) -> 'float':
        '''float: 'TangentialTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialTilt

    @property
    def radial_tilt(self) -> 'float':
        '''float: 'RadialTilt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialTilt

    @property
    def relative_tangential_deflection(self) -> 'float':
        '''float: 'RelativeTangentialDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeTangentialDeflection

    @property
    def relative_radial_deflection(self) -> 'float':
        '''float: 'RelativeRadialDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeRadialDeflection

    @property
    def relative_axial_deflection(self) -> 'float':
        '''float: 'RelativeAxialDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeAxialDeflection

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Angle
