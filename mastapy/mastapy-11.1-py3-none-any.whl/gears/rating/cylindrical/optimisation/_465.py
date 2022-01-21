'''_465.py

SafetyFactorOptimisationStepResult
'''


from mastapy.gears.rating import _334
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SAFETY_FACTOR_OPTIMISATION_STEP_RESULT = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.Optimisation', 'SafetyFactorOptimisationStepResult')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyFactorOptimisationStepResult',)


class SafetyFactorOptimisationStepResult(_0.APIBase):
    '''SafetyFactorOptimisationStepResult

    This is a mastapy class.
    '''

    TYPE = _SAFETY_FACTOR_OPTIMISATION_STEP_RESULT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SafetyFactorOptimisationStepResult.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factors(self) -> '_334.SafetyFactorResults':
        '''SafetyFactorResults: 'SafetyFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_334.SafetyFactorResults)(self.wrapped.SafetyFactors) if self.wrapped.SafetyFactors is not None else None

    @property
    def normalised_safety_factors(self) -> '_334.SafetyFactorResults':
        '''SafetyFactorResults: 'NormalisedSafetyFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_334.SafetyFactorResults)(self.wrapped.NormalisedSafetyFactors) if self.wrapped.NormalisedSafetyFactors is not None else None
