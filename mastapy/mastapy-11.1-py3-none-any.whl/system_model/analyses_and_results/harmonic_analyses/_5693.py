'''_5693.py

ConceptGearHarmonicAnalysis
'''


from mastapy.system_model.part_model.gears import _2261
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6555
from mastapy.system_model.analyses_and_results.system_deflections import _2457
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5735
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'ConceptGearHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearHarmonicAnalysis',)


class ConceptGearHarmonicAnalysis(_5735.GearHarmonicAnalysis):
    '''ConceptGearHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2261.ConceptGear':
        '''ConceptGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2261.ConceptGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6555.ConceptGearLoadCase':
        '''ConceptGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6555.ConceptGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2457.ConceptGearSystemDeflection':
        '''ConceptGearSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2457.ConceptGearSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
