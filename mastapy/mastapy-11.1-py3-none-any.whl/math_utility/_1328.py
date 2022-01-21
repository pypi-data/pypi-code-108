'''_1328.py

SinCurve
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SIN_CURVE = python_net_import('SMT.MastaAPI.MathUtility', 'SinCurve')


__docformat__ = 'restructuredtext en'
__all__ = ('SinCurve',)


class SinCurve(_0.APIBase):
    '''SinCurve

    This is a mastapy class.
    '''

    TYPE = _SIN_CURVE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SinCurve.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def starting_angle(self) -> 'float':
        '''float: 'StartingAngle' is the original name of this property.'''

        return self.wrapped.StartingAngle

    @starting_angle.setter
    def starting_angle(self, value: 'float'):
        self.wrapped.StartingAngle = float(value) if value else 0.0

    @property
    def number_of_cycles(self) -> 'float':
        '''float: 'NumberOfCycles' is the original name of this property.'''

        return self.wrapped.NumberOfCycles

    @number_of_cycles.setter
    def number_of_cycles(self, value: 'float'):
        self.wrapped.NumberOfCycles = float(value) if value else 0.0
