'''_1822.py

SMTRibStressResults
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SMT_RIB_STRESS_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'SMTRibStressResults')


__docformat__ = 'restructuredtext en'
__all__ = ('SMTRibStressResults',)


class SMTRibStressResults(_0.APIBase):
    '''SMTRibStressResults

    This is a mastapy class.
    '''

    TYPE = _SMT_RIB_STRESS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SMTRibStressResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factor(self) -> 'float':
        '''float: 'SafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactor

    @property
    def maximum_rib_load(self) -> 'float':
        '''float: 'MaximumRibLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRibLoad
