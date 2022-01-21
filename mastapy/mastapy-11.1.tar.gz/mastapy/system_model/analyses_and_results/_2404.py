'''_2404.py

CompoundDynamicModelForHarmonicAnalysis
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_DYNAMIC_MODEL_FOR_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundDynamicModelForHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundDynamicModelForHarmonicAnalysis',)


class CompoundDynamicModelForHarmonicAnalysis(_2359.CompoundAnalysis):
    '''CompoundDynamicModelForHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_DYNAMIC_MODEL_FOR_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundDynamicModelForHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
