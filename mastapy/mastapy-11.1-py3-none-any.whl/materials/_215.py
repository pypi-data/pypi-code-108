'''_215.py

AirProperties
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_AIR_PROPERTIES = python_net_import('SMT.MastaAPI.Materials', 'AirProperties')


__docformat__ = 'restructuredtext en'
__all__ = ('AirProperties',)


class AirProperties(_0.APIBase):
    '''AirProperties

    This is a mastapy class.
    '''

    TYPE = _AIR_PROPERTIES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AirProperties.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def specific_gas_constant(self) -> 'float':
        '''float: 'SpecificGasConstant' is the original name of this property.'''

        return self.wrapped.SpecificGasConstant

    @specific_gas_constant.setter
    def specific_gas_constant(self, value: 'float'):
        self.wrapped.SpecificGasConstant = float(value) if value else 0.0

    @property
    def pressure(self) -> 'float':
        '''float: 'Pressure' is the original name of this property.'''

        return self.wrapped.Pressure

    @pressure.setter
    def pressure(self, value: 'float'):
        self.wrapped.Pressure = float(value) if value else 0.0

    @property
    def adiabatic_index(self) -> 'float':
        '''float: 'AdiabaticIndex' is the original name of this property.'''

        return self.wrapped.AdiabaticIndex

    @adiabatic_index.setter
    def adiabatic_index(self, value: 'float'):
        self.wrapped.AdiabaticIndex = float(value) if value else 0.0
