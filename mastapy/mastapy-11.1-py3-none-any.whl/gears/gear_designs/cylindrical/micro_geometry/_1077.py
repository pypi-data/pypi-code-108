'''_1077.py

ReliefWithDeviation
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RELIEF_WITH_DEVIATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'ReliefWithDeviation')


__docformat__ = 'restructuredtext en'
__all__ = ('ReliefWithDeviation',)


class ReliefWithDeviation(_0.APIBase):
    '''ReliefWithDeviation

    This is a mastapy class.
    '''

    TYPE = _RELIEF_WITH_DEVIATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ReliefWithDeviation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def section(self) -> 'str':
        '''str: 'Section' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Section

    @property
    def relief(self) -> 'float':
        '''float: 'Relief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Relief

    @property
    def upper_limit(self) -> 'float':
        '''float: 'UpperLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UpperLimit

    @property
    def lower_limit(self) -> 'float':
        '''float: 'LowerLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LowerLimit
