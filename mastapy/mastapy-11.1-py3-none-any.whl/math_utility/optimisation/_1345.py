'''_1345.py

ParetoOptimisationFilter
'''


from mastapy.math_utility import _1287
from mastapy._internal import constructor
from mastapy.math_utility.measured_ranges import _1364
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PARETO_OPTIMISATION_FILTER = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'ParetoOptimisationFilter')


__docformat__ = 'restructuredtext en'
__all__ = ('ParetoOptimisationFilter',)


class ParetoOptimisationFilter(_0.APIBase):
    '''ParetoOptimisationFilter

    This is a mastapy class.
    '''

    TYPE = _PARETO_OPTIMISATION_FILTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParetoOptimisationFilter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def filter_range(self) -> '_1287.Range':
        '''Range: 'FilterRange' is the original name of this property.'''

        if _1287.Range.TYPE not in self.wrapped.FilterRange.__class__.__mro__:
            raise CastException('Failed to cast filter_range to Range. Expected: {}.'.format(self.wrapped.FilterRange.__class__.__qualname__))

        return constructor.new_override(self.wrapped.FilterRange.__class__)(self.wrapped.FilterRange) if self.wrapped.FilterRange is not None else None

    @filter_range.setter
    def filter_range(self, value: '_1287.Range'):
        value = value.wrapped if value else None
        self.wrapped.FilterRange = value

    @property
    def property_(self) -> 'str':
        '''str: 'Property' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Property
