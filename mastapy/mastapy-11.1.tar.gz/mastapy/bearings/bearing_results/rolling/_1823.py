'''_1823.py

StressAtPosition
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_STRESS_AT_POSITION = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'StressAtPosition')


__docformat__ = 'restructuredtext en'
__all__ = ('StressAtPosition',)


class StressAtPosition(_0.APIBase):
    '''StressAtPosition

    This is a mastapy class.
    '''

    TYPE = _STRESS_AT_POSITION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StressAtPosition.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def position(self) -> 'float':
        '''float: 'Position' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Position

    @property
    def stress(self) -> 'float':
        '''float: 'Stress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Stress
