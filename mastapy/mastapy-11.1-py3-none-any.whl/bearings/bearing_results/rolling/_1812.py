'''_1812.py

MaximumStaticContactStressResultsAbstract
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MAXIMUM_STATIC_CONTACT_STRESS_RESULTS_ABSTRACT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'MaximumStaticContactStressResultsAbstract')


__docformat__ = 'restructuredtext en'
__all__ = ('MaximumStaticContactStressResultsAbstract',)


class MaximumStaticContactStressResultsAbstract(_0.APIBase):
    '''MaximumStaticContactStressResultsAbstract

    This is a mastapy class.
    '''

    TYPE = _MAXIMUM_STATIC_CONTACT_STRESS_RESULTS_ABSTRACT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MaximumStaticContactStressResultsAbstract.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def stress_ratio_inner(self) -> 'float':
        '''float: 'StressRatioInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressRatioInner

    @property
    def stress_ratio_outer(self) -> 'float':
        '''float: 'StressRatioOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressRatioOuter

    @property
    def safety_factor_inner(self) -> 'float':
        '''float: 'SafetyFactorInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorInner

    @property
    def safety_factor_outer(self) -> 'float':
        '''float: 'SafetyFactorOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorOuter
