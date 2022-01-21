'''_5851.py

ResultsForSingleDegreeOfFreedomOfResponseOfNodeInHarmonic
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RESULTS_FOR_SINGLE_DEGREE_OF_FREEDOM_OF_RESPONSE_OF_NODE_IN_HARMONIC = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'ResultsForSingleDegreeOfFreedomOfResponseOfNodeInHarmonic')


__docformat__ = 'restructuredtext en'
__all__ = ('ResultsForSingleDegreeOfFreedomOfResponseOfNodeInHarmonic',)


class ResultsForSingleDegreeOfFreedomOfResponseOfNodeInHarmonic(_0.APIBase):
    '''ResultsForSingleDegreeOfFreedomOfResponseOfNodeInHarmonic

    This is a mastapy class.
    '''

    TYPE = _RESULTS_FOR_SINGLE_DEGREE_OF_FREEDOM_OF_RESPONSE_OF_NODE_IN_HARMONIC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ResultsForSingleDegreeOfFreedomOfResponseOfNodeInHarmonic.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def max(self) -> 'float':
        '''float: 'Max' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Max

    @property
    def frequency_of_max(self) -> 'float':
        '''float: 'FrequencyOfMax' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrequencyOfMax

    @property
    def integral(self) -> 'float':
        '''float: 'Integral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Integral
