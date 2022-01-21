'''_2368.py

DynamicModelForHarmonicAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_DYNAMIC_MODEL_FOR_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'DynamicModelForHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicModelForHarmonicAnalysis',)


class DynamicModelForHarmonicAnalysis(_2360.SingleAnalysis):
    '''DynamicModelForHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_MODEL_FOR_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicModelForHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
