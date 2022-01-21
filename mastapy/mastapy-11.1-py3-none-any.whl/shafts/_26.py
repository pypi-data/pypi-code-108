'''_26.py

ShaftPointStress
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1330
from mastapy._internal.python_net import python_net_import

_SHAFT_POINT_STRESS = python_net_import('SMT.MastaAPI.Shafts', 'ShaftPointStress')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftPointStress',)


class ShaftPointStress(_1330.StressPoint):
    '''ShaftPointStress

    This is a mastapy class.
    '''

    TYPE = _SHAFT_POINT_STRESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftPointStress.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bending_stress(self) -> 'float':
        '''float: 'BendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingStress

    @property
    def angle_of_max_bending_stress(self) -> 'float':
        '''float: 'AngleOfMaxBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleOfMaxBendingStress

    @property
    def von_mises_stress_max(self) -> 'float':
        '''float: 'VonMisesStressMax' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VonMisesStressMax

    @property
    def maximum_principal_stress(self) -> 'float':
        '''float: 'MaximumPrincipalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPrincipalStress

    @property
    def minimum_principal_stress(self) -> 'float':
        '''float: 'MinimumPrincipalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumPrincipalStress
