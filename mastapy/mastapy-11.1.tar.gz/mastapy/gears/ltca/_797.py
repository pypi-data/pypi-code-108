'''_797.py

GearFilletNodeStressResults
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_FILLET_NODE_STRESS_RESULTS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearFilletNodeStressResults')


__docformat__ = 'restructuredtext en'
__all__ = ('GearFilletNodeStressResults',)


class GearFilletNodeStressResults(_0.APIBase):
    '''GearFilletNodeStressResults

    This is a mastapy class.
    '''

    TYPE = _GEAR_FILLET_NODE_STRESS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearFilletNodeStressResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def fillet_column_index(self) -> 'int':
        '''int: 'FilletColumnIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilletColumnIndex

    @property
    def fillet_row_index(self) -> 'int':
        '''int: 'FilletRowIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilletRowIndex

    @property
    def maximum_tensile_principal_stress(self) -> 'float':
        '''float: 'MaximumTensilePrincipalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTensilePrincipalStress

    @property
    def von_mises_stress(self) -> 'float':
        '''float: 'VonMisesStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VonMisesStress

    @property
    def x_component(self) -> 'float':
        '''float: 'XComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.XComponent

    @property
    def y_component(self) -> 'float':
        '''float: 'YComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YComponent

    @property
    def z_component(self) -> 'float':
        '''float: 'ZComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ZComponent

    @property
    def xy_shear_stress(self) -> 'float':
        '''float: 'XYShearStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.XYShearStress

    @property
    def yz_shear_stress(self) -> 'float':
        '''float: 'YZShearStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YZShearStress

    @property
    def xz_shear_stress(self) -> 'float':
        '''float: 'XZShearStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.XZShearStress

    @property
    def first_principal_stress(self) -> 'float':
        '''float: 'FirstPrincipalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FirstPrincipalStress

    @property
    def second_principal_stress(self) -> 'float':
        '''float: 'SecondPrincipalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SecondPrincipalStress

    @property
    def third_principal_stress(self) -> 'float':
        '''float: 'ThirdPrincipalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThirdPrincipalStress

    @property
    def stress_intensity(self) -> 'float':
        '''float: 'StressIntensity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressIntensity
