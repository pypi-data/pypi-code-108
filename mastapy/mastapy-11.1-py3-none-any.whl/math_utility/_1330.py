'''_1330.py

StressPoint
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_STRESS_POINT = python_net_import('SMT.MastaAPI.MathUtility', 'StressPoint')


__docformat__ = 'restructuredtext en'
__all__ = ('StressPoint',)


class StressPoint(_0.APIBase):
    '''StressPoint

    This is a mastapy class.
    '''

    TYPE = _STRESS_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StressPoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial_stress(self) -> 'float':
        '''float: 'AxialStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialStress

    @property
    def x_bending_stress(self) -> 'float':
        '''float: 'XBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.XBendingStress

    @property
    def y_bending_stress(self) -> 'float':
        '''float: 'YBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YBendingStress

    @property
    def torsional_stress(self) -> 'float':
        '''float: 'TorsionalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorsionalStress
