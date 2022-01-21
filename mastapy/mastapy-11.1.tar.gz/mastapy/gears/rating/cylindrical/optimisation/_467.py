'''_467.py

SafetyFactorOptimisationStepResultNumber
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.optimisation import _465
from mastapy._internal.python_net import python_net_import

_SAFETY_FACTOR_OPTIMISATION_STEP_RESULT_NUMBER = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.Optimisation', 'SafetyFactorOptimisationStepResultNumber')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyFactorOptimisationStepResultNumber',)


class SafetyFactorOptimisationStepResultNumber(_465.SafetyFactorOptimisationStepResult):
    '''SafetyFactorOptimisationStepResultNumber

    This is a mastapy class.
    '''

    TYPE = _SAFETY_FACTOR_OPTIMISATION_STEP_RESULT_NUMBER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SafetyFactorOptimisationStepResultNumber.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def value(self) -> 'float':
        '''float: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Value
