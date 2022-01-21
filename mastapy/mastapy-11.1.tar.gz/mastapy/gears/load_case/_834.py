'''_834.py

GearSetLoadCaseBase
'''


from mastapy._internal import constructor
from mastapy.gears.analysis import _1170
from mastapy._internal.python_net import python_net_import

_GEAR_SET_LOAD_CASE_BASE = python_net_import('SMT.MastaAPI.Gears.LoadCase', 'GearSetLoadCaseBase')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetLoadCaseBase',)


class GearSetLoadCaseBase(_1170.GearSetDesignAnalysis):
    '''GearSetLoadCaseBase

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_LOAD_CASE_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetLoadCaseBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def unit_duration(self) -> 'float':
        '''float: 'UnitDuration' is the original name of this property.'''

        return self.wrapped.UnitDuration

    @unit_duration.setter
    def unit_duration(self, value: 'float'):
        self.wrapped.UnitDuration = float(value) if value else 0.0

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''
