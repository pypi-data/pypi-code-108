'''_833.py

GearLoadCaseBase
'''


from mastapy._internal import constructor
from mastapy.gears.analysis import _1162
from mastapy._internal.python_net import python_net_import

_GEAR_LOAD_CASE_BASE = python_net_import('SMT.MastaAPI.Gears.LoadCase', 'GearLoadCaseBase')


__docformat__ = 'restructuredtext en'
__all__ = ('GearLoadCaseBase',)


class GearLoadCaseBase(_1162.GearDesignAnalysis):
    '''GearLoadCaseBase

    This is a mastapy class.
    '''

    TYPE = _GEAR_LOAD_CASE_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearLoadCaseBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sump_temperature(self) -> 'float':
        '''float: 'SumpTemperature' is the original name of this property.'''

        return self.wrapped.SumpTemperature

    @sump_temperature.setter
    def sump_temperature(self, value: 'float'):
        self.wrapped.SumpTemperature = float(value) if value else 0.0

    @property
    def duration(self) -> 'float':
        '''float: 'Duration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Duration

    @property
    def gear_temperature(self) -> 'float':
        '''float: 'GearTemperature' is the original name of this property.'''

        return self.wrapped.GearTemperature

    @gear_temperature.setter
    def gear_temperature(self, value: 'float'):
        self.wrapped.GearTemperature = float(value) if value else 0.0
