'''_463.py

OptimisationResultsPair
'''


from typing import Generic, TypeVar

from mastapy.gears.rating.cylindrical.optimisation import _464, _465
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_OPTIMISATION_RESULTS_PAIR = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.Optimisation', 'OptimisationResultsPair')


__docformat__ = 'restructuredtext en'
__all__ = ('OptimisationResultsPair',)


T = TypeVar('T', bound='_465.SafetyFactorOptimisationStepResult')


class OptimisationResultsPair(_0.APIBase, Generic[T]):
    '''OptimisationResultsPair

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _OPTIMISATION_RESULTS_PAIR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OptimisationResultsPair.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def results_without_warnings(self) -> '_464.SafetyFactorOptimisationResults[T]':
        '''SafetyFactorOptimisationResults[T]: 'ResultsWithoutWarnings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_464.SafetyFactorOptimisationResults)[T](self.wrapped.ResultsWithoutWarnings) if self.wrapped.ResultsWithoutWarnings is not None else None

    @property
    def results(self) -> '_464.SafetyFactorOptimisationResults[T]':
        '''SafetyFactorOptimisationResults[T]: 'Results' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_464.SafetyFactorOptimisationResults)[T](self.wrapped.Results) if self.wrapped.Results is not None else None
