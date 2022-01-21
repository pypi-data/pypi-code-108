'''_1347.py

ParetoOptimisationOutput
'''


from mastapy._internal import constructor
from mastapy.math_utility.optimisation import _1353
from mastapy._internal.python_net import python_net_import

_PARETO_OPTIMISATION_OUTPUT = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'ParetoOptimisationOutput')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoOptimisationOutput',)


class ParetoOptimisationOutput(_1353.ParetoOptimistaionVariable):
    '''ParetoOptimisationOutput

    This is a mastapy class.
    '''

    TYPE = _PARETO_OPTIMISATION_OUTPUT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoOptimisationOutput.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def exclude_from_dominant_candidates_search(self) -> 'bool':
        '''bool: 'ExcludeFromDominantCandidatesSearch' is the original name of this property.'''

        return self.wrapped.ExcludeFromDominantCandidatesSearch

    @exclude_from_dominant_candidates_search.setter
    def exclude_from_dominant_candidates_search(self, value: 'bool'):
        self.wrapped.ExcludeFromDominantCandidatesSearch = bool(value) if value else False

    @property
    def use_original_design_value(self) -> 'bool':
        '''bool: 'UseOriginalDesignValue' is the original name of this property.'''

        return self.wrapped.UseOriginalDesignValue

    @use_original_design_value.setter
    def use_original_design_value(self, value: 'bool'):
        self.wrapped.UseOriginalDesignValue = bool(value) if value else False

    @property
    def percent(self) -> 'float':
        '''float: 'Percent' is the original name of this property.'''

        return self.wrapped.Percent

    @percent.setter
    def percent(self, value: 'float'):
        self.wrapped.Percent = float(value) if value else 0.0
