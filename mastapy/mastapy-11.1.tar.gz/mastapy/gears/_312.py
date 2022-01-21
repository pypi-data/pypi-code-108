'''_312.py

SpecificationForTheEffectOfOilKinematicViscosity
'''


from mastapy._internal import constructor
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_SPECIFICATION_FOR_THE_EFFECT_OF_OIL_KINEMATIC_VISCOSITY = python_net_import('SMT.MastaAPI.Gears', 'SpecificationForTheEffectOfOilKinematicViscosity')


__docformat__ = 'restructuredtext en'
__all__ = ('SpecificationForTheEffectOfOilKinematicViscosity',)


class SpecificationForTheEffectOfOilKinematicViscosity(_1382.IndependentReportablePropertiesBase['SpecificationForTheEffectOfOilKinematicViscosity']):
    '''SpecificationForTheEffectOfOilKinematicViscosity

    This is a mastapy class.
    '''

    TYPE = _SPECIFICATION_FOR_THE_EFFECT_OF_OIL_KINEMATIC_VISCOSITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpecificationForTheEffectOfOilKinematicViscosity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def slope_of_linear_equation(self) -> 'float':
        '''float: 'SlopeOfLinearEquation' is the original name of this property.'''

        return self.wrapped.SlopeOfLinearEquation

    @slope_of_linear_equation.setter
    def slope_of_linear_equation(self, value: 'float'):
        self.wrapped.SlopeOfLinearEquation = float(value) if value else 0.0

    @property
    def intercept_of_linear_equation(self) -> 'float':
        '''float: 'InterceptOfLinearEquation' is the original name of this property.'''

        return self.wrapped.InterceptOfLinearEquation

    @intercept_of_linear_equation.setter
    def intercept_of_linear_equation(self, value: 'float'):
        self.wrapped.InterceptOfLinearEquation = float(value) if value else 0.0

    @property
    def condition(self) -> 'str':
        '''str: 'Condition' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Condition
