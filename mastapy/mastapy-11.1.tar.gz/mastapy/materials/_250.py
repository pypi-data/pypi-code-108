'''_250.py

SNCurvePoint
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SN_CURVE_POINT = python_net_import('SMT.MastaAPI.Materials', 'SNCurvePoint')


__docformat__ = 'restructuredtext en'
__all__ = ('SNCurvePoint',)


class SNCurvePoint(_0.APIBase):
    '''SNCurvePoint

    This is a mastapy class.
    '''

    TYPE = _SN_CURVE_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SNCurvePoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_cycles(self) -> 'float':
        '''float: 'NumberOfCycles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfCycles

    @property
    def stress(self) -> 'float':
        '''float: 'Stress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Stress
