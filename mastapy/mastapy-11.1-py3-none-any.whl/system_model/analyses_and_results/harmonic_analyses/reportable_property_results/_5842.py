'''_5842.py

ResultsForMultipleOrders
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RESULTS_FOR_MULTIPLE_ORDERS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'ResultsForMultipleOrders')


__docformat__ = 'restructuredtext en'
__all__ = ('ResultsForMultipleOrders',)


class ResultsForMultipleOrders(_0.APIBase):
    '''ResultsForMultipleOrders

    This is a mastapy class.
    '''

    TYPE = _RESULTS_FOR_MULTIPLE_ORDERS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ResultsForMultipleOrders.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def combined_excitations_harmonics_and_orders(self) -> 'str':
        '''str: 'CombinedExcitationsHarmonicsAndOrders' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedExcitationsHarmonicsAndOrders
