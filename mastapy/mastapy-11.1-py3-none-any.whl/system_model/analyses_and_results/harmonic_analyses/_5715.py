'''_5715.py

DatumHarmonicAnalysis
'''


from mastapy.system_model.part_model import _2190
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6583
from mastapy.system_model.analyses_and_results.system_deflections import _2486
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5689
from mastapy._internal.python_net import python_net_import

_DATUM_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'DatumHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DatumHarmonicAnalysis',)


class DatumHarmonicAnalysis(_5689.ComponentHarmonicAnalysis):
    '''DatumHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _DATUM_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatumHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2190.Datum':
        '''Datum: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2190.Datum)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6583.DatumLoadCase':
        '''DatumLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6583.DatumLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2486.DatumSystemDeflection':
        '''DatumSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2486.DatumSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
